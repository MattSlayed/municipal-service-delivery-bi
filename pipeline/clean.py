"""Scope, validate and flag service requests.

Rows are removed only when provably invalid, and every removed row is kept in the quarantine
table with a reason code, so that in-scope rows = clean rows + quarantined rows. Doubtful rows
are flagged, never removed.
"""

import pandas as pd

from . import config


def load_raw(path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)


def select_scope(raw: pd.DataFrame) -> pd.DataFrame:
    in_scope = raw["directorate"].eq(config.DIRECTORATE) & raw["code_group"].isin(
        config.FIELD_CODE_GROUPS
    )
    return raw.loc[in_scope].copy()


def to_sast(timestamps: pd.Series) -> pd.Series:
    """Parse offset timestamps and return naive SAST wall-clock times (what Power BI expects)."""
    return (
        pd.to_datetime(timestamps, utc=True)
        .dt.tz_convert(config.TIMEZONE)
        .dt.tz_localize(None)
    )


def clean(scoped: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (clean rows with flags, quarantined rows with reason_code)."""
    df = scoped.copy()
    df["created_at"] = to_sast(df["creation_timestamp"])
    df["completed_at"] = to_sast(df["completion_timestamp"])
    df["h3_level8_index"] = df["h3_level8_index"].fillna(config.UNLOCATED_HEX)

    reason = pd.Series(pd.NA, index=df.index, dtype="string")
    reason[df["notification_number"].duplicated(keep="first")] = "DUPLICATE_RECORD"
    negative = df["completed_at"] < df["created_at"]
    reason[negative & reason.isna()] = "NEGATIVE_DURATION"

    quarantine = df.loc[reason.notna()].assign(reason_code=reason[reason.notna()])
    kept = df.loc[reason.isna()].copy()

    seconds = (kept["completed_at"] - kept["created_at"]).dt.total_seconds()
    kept["days_to_complete"] = seconds / 86400
    kept["is_admin_closure"] = seconds.lt(config.ADMIN_CLOSURE_SECONDS)
    kept["is_located"] = kept["h3_level8_index"].ne(config.UNLOCATED_HEX)
    kept["is_likely_repeat"] = flag_likely_repeats(kept)
    return kept, quarantine


def flag_likely_repeats(df: pd.DataFrame) -> pd.Series:
    """Flag later reports of the same fault type in the same hexagon on the same SAST day.

    The first report is not flagged. Unlocated requests are never flagged: sharing the
    placeholder hexagon says nothing about sharing a fault.
    """
    located = df.loc[df["is_located"]].sort_values("created_at", kind="stable")
    repeat = located.assign(day=located["created_at"].dt.normalize()).duplicated(
        ["code", "h3_level8_index", "day"], keep="first"
    )
    return repeat.reindex(df.index, fill_value=False)
