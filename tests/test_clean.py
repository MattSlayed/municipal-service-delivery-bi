import pandas as pd
import pytest

from pipeline import clean

COLUMNS = ["notification_number", "creation_timestamp", "completion_timestamp", "directorate",
           "department", "branch", "section", "code_group", "code", "official_suburb",
           "h3_level8_index"]


def request(number, created, completed=None, code="Burst Pipe", hexagon="88ad361133fffff",
            directorate="WATER AND SANITATION", code_group="WATER"):
    return [number, created, completed, directorate, "Distribution Services", "Reticulation",
            "Reticulation Water Distribution", code_group, code, "ATHLONE", hexagon]


@pytest.fixture
def scoped():
    rows = [
        request("1", "2020-03-02 08:00:00+02:00", "2020-03-04 08:00:00+02:00"),       # normal
        request("2", "2020-03-02 09:00:00+02:00", "2020-03-01 09:00:00+02:00"),       # negative
        request("2", "2020-03-02 09:00:00+02:00", "2020-03-03 09:00:00+02:00"),       # duplicate id
        request("3", "2020-03-02 10:00:00+02:00", "2020-03-02 10:04:59+02:00", code="Leak"),  # admin
        request("4", "2020-03-02 11:00:00+02:00", None, code="Leak", hexagon="88ad3610e9fffff"),  # open
        request("5", "2020-03-02 23:30:00+02:00", "2020-03-05 08:00:00+02:00"),       # repeat of 1
        request("6", "2020-03-03 00:30:00+02:00", "2020-03-05 08:00:00+02:00"),       # next SAST day
        request("7", "2020-03-02 08:00:00+02:00", "2020-03-06 08:00:00+02:00", hexagon="0"),
        request("8", "2020-03-02 09:00:00+02:00", "2020-03-06 08:00:00+02:00", hexagon="0"),
    ]
    return pd.DataFrame(rows, columns=COLUMNS)


def test_scope_keeps_only_water_and_sanitation_field_work():
    raw = pd.DataFrame([
        request("1", "2020-01-01 00:00:00+02:00"),
        request("2", "2020-01-01 00:00:00+02:00", directorate="ENERGY"),
        request("3", "2020-01-01 00:00:00+02:00", code_group="WATER AND SANITATION OR METER QUERIES"),
        request("4", "2020-01-01 00:00:00+02:00", code_group="WATER  - INFORMAL SETTLEMENTS"),
    ], columns=COLUMNS)
    assert clean.select_scope(raw)["notification_number"].tolist() == ["1", "4"]


def test_every_row_is_either_kept_or_quarantined(scoped):
    kept, quarantine = clean.clean(scoped)
    assert len(kept) + len(quarantine) == len(scoped)


def test_quarantine_reasons(scoped):
    _, quarantine = clean.clean(scoped)
    reasons = dict(zip(quarantine.index, quarantine["reason_code"]))
    assert reasons == {1: "NEGATIVE_DURATION", 2: "DUPLICATE_RECORD"}


def test_admin_closure_is_under_five_minutes_only(scoped):
    kept, _ = clean.clean(scoped)
    assert kept.loc[kept["is_admin_closure"], "notification_number"].tolist() == ["3"]


def test_open_request_is_not_an_admin_closure(scoped):
    kept, _ = clean.clean(scoped)
    open_request = kept.loc[kept["notification_number"] == "4"].iloc[0]
    assert pd.isna(open_request["completed_at"])
    assert not open_request["is_admin_closure"]


def test_likely_repeat_flags_later_report_same_fault_hexagon_and_sast_day(scoped):
    kept, _ = clean.clean(scoped)
    assert kept.loc[kept["is_likely_repeat"], "notification_number"].tolist() == ["5"]


def test_unlocated_requests_are_never_likely_repeats(scoped):
    kept, _ = clean.clean(scoped)
    unlocated = kept.loc[~kept["is_located"]]
    assert unlocated["notification_number"].tolist() == ["7", "8"]
    assert not unlocated["is_likely_repeat"].any()


def test_timestamps_are_converted_to_naive_sast():
    parsed = clean.to_sast(pd.Series(["2020-01-01 00:30:00+02:00", "2019-12-31 22:30:00+00:00"]))
    assert parsed.tolist() == [pd.Timestamp("2020-01-01 00:30:00")] * 2
