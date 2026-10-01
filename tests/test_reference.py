import json

import pandas as pd
import pytest

from pipeline import config, reference

T = reference.as_at_end("2020-03-31")  # a Tuesday


def frame(rows):
    df = pd.DataFrame(rows, columns=["section", "created_at", "completed_at", "is_admin_closure"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["completed_at"] = pd.to_datetime(df["completed_at"])
    return df


def test_as_at_is_the_last_second_of_the_day():
    assert T == pd.Timestamp("2020-03-31 23:59:59")


def test_open_at_boundaries():
    df = frame([
        ("A", "2020-03-31 23:59:59", None, False),                   # created exactly at t: open
        ("A", "2020-03-01 00:00:00", "2020-03-31 23:59:59", False),  # completed exactly at t: closed
        ("A", "2020-03-01 00:00:00", "2020-04-01 00:00:00", False),  # completed after t: open
        ("A", "2020-04-01 00:00:00", None, False),                   # created after t: not yet
    ])
    assert reference.open_at(df, T).tolist() == [True, False, True, False]


def test_four_week_window_uses_only_full_weeks():
    start, end = reference.four_week_window(T)
    assert (start, end) == (pd.Timestamp("2020-03-02"), pd.Timestamp("2020-03-30"))


def test_four_week_window_includes_the_week_ending_on_a_sunday():
    start, end = reference.four_week_window(reference.as_at_end("2020-03-29"))
    assert (start, end) == (pd.Timestamp("2020-03-02"), pd.Timestamp("2020-03-30"))


def test_age_is_whole_days_elapsed():
    df = frame([("A", "2020-03-30 23:00:00", None, False), ("A", "2020-03-31 00:30:00", None, False)])
    assert reference.age_days(df, T).tolist() == [1, 0]


def test_active_and_stuck_split_at_90_days():
    df = frame([
        ("A", "2020-01-01 00:00:00", None, False),  # 90 whole days at t: still active
        ("A", "2019-12-31 23:00:00", None, False),  # 91 whole days at t: stuck
    ])
    assert reference.active_at(df, T).tolist() == [True, False]
    assert reference.stuck_at(df, T).tolist() == [False, True]


def test_weeks_to_clear_and_flag():
    completions = [("A", "2020-02-20", f"2020-03-{d:02d} 12:00", False) for d in range(2, 30)]  # 28 = 7/week
    admin = [("A", "2020-03-10", "2020-03-10 00:01", True)] * 50  # never counted as throughput
    backlog = [("A", "2020-03-15", None, False)] * 28  # 28 active / 7 per week = 4 weeks
    stuck = [("A", "2019-11-01", None, False)] * 100  # over 90 days: excluded from weeks to clear
    table = reference.weeks_to_clear(frame(completions + admin + backlog + stuck), T, "section", {"A"})
    row = table.loc["A"]
    assert row["avg_weekly_completions"] == 7
    assert row["active"] == 28
    assert row["weeks_to_clear"] == 4
    assert row["flag"]  # 4 > default threshold of 3


def test_weeks_to_clear_at_the_threshold_is_not_flagged():
    completions = [("A", "2020-02-20", f"2020-03-{d:02d} 12:00", False) for d in range(2, 30)]
    backlog = [("A", "2020-03-15", None, False)] * 21  # exactly 3 weeks
    row = reference.weeks_to_clear(frame(completions + backlog), T, "section", {"A"}).loc["A"]
    assert row["weeks_to_clear"] == config.DEFAULT_THRESHOLD_WEEKS
    assert not row["flag"]


def test_weeks_to_clear_is_blank_below_minimum_throughput():
    completions = [("B", "2020-02-20", "2020-03-10 12:00", False)] * (4 * config.MIN_WEEKLY_COMPLETIONS - 1)
    table = reference.weeks_to_clear(frame(completions + [("B", "2020-03-15", None, False)]), T, "section", {"B"})
    assert pd.isna(table.loc["B", "weeks_to_clear"])
    assert not table.loc["B", "flag"]


def test_administrative_section_is_never_flagged():
    completions = [("Billing", "2020-02-20", f"2020-03-{d:02d} 12:00", False) for d in range(2, 30)]
    backlog = [("Billing", "2020-03-15", None, False)] * 70  # 10 weeks to clear
    row = reference.weeks_to_clear(frame(completions + backlog), T, "section", {"A"}).loc["Billing"]
    assert row["weeks_to_clear"] == 10
    assert not row["field_crew"]
    assert not row["flag"]


def test_unknown_suburb_is_shown_beside_the_rank_not_in_it():
    rows = (
        [("A", "2020-03-15", None, False, config.UNKNOWN_SUBURB)] * 5
        + [("A", "2020-03-15", None, False, "GUGULETU")] * 3
        + [("A", "2020-03-15", None, False, "PHILIPPI")] * 2
    )
    df = pd.DataFrame(rows, columns=["section", "created_at", "completed_at", "is_admin_closure", "official_suburb"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["completed_at"] = pd.to_datetime(df["completed_at"])
    ranked = reference.suburb_rank(df, T, ["A"])["A"]
    assert [row["official_suburb"] for row in ranked] == ["GUGULETU", "PHILIPPI"]
    assert reference.unknown_suburb_active(df, T, ["A"]) == {"A": 5}


REFERENCE_FILE = config.PROCESSED_DIR / "reference_values.json"


@pytest.mark.skipif(not REFERENCE_FILE.exists(), reason="run the pipeline first")
def test_real_data_reconciles():
    transparency = json.loads(REFERENCE_FILE.read_text())["transparency"]
    assert transparency["reconciles"]
    assert transparency["in_scope_rows"] == transparency["clean_rows"] + transparency["quarantined_rows"]
