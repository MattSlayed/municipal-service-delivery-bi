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


def test_weeks_to_clear_and_flag():
    completions = [("A", "2020-02-20", f"2020-03-{d:02d} 12:00", False) for d in range(2, 30)]  # 28 = 7/week
    admin = [("A", "2020-03-10", "2020-03-10 00:01", True)] * 50  # never counted as throughput
    backlog = [("A", "2020-03-15", None, False)] * 21  # 21 open / 7 per week = 3 weeks
    table = reference.weeks_to_clear(frame(completions + admin + backlog), T, "section")
    row = table.loc["A"]
    assert row["avg_weekly_completions"] == 7
    assert row["weeks_to_clear"] == 3
    assert row["flag"]  # 3 > default threshold of 2


def test_weeks_to_clear_is_blank_below_minimum_throughput():
    completions = [("B", "2020-02-20", "2020-03-10 12:00", False)] * (4 * config.MIN_WEEKLY_COMPLETIONS - 1)
    table = reference.weeks_to_clear(frame(completions + [("B", "2020-03-15", None, False)]), T, "section")
    assert pd.isna(table.loc["B", "weeks_to_clear"])
    assert not table.loc["B", "flag"]


REFERENCE_FILE = config.PROCESSED_DIR / "reference_values.json"


@pytest.mark.skipif(not REFERENCE_FILE.exists(), reason="run the pipeline first")
def test_real_data_reconciles():
    transparency = json.loads(REFERENCE_FILE.read_text())["transparency"]
    assert transparency["reconciles"]
    assert transparency["in_scope_rows"] == transparency["clean_rows"] + transparency["quarantined_rows"]
