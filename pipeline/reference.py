"""Compute the expected value of every v1.0 measure, independently of Power BI.

The DAX measures are tested against these numbers (spec: measures.md). Keep the logic here
plain and literal: it is the yardstick, not an optimisation.
"""

import json

import numpy as np
import pandas as pd

from . import config

WEEK = pd.Timedelta(days=7)


def as_at_end(date: str) -> pd.Timestamp:
    return pd.Timestamp(date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)


def week_start(timestamps: pd.Series) -> pd.Series:
    days = timestamps.dt.normalize()
    return days - pd.to_timedelta(days.dt.weekday, unit="D")


def open_at(df: pd.DataFrame, t: pd.Timestamp) -> pd.Series:
    """Created at or before t, and not completed by t."""
    return (df["created_at"] <= t) & (df["completed_at"].isna() | (df["completed_at"] > t))


def age_days(df: pd.DataFrame, t: pd.Timestamp) -> pd.Series:
    """Whole days elapsed since creation (floor). With t at 23:59:59 this equals calendar days."""
    return (t - df["created_at"]).dt.days


def active_at(df: pd.DataFrame, t: pd.Timestamp) -> pd.Series:
    """Open at t and no older than the active window; older open work is stuck."""
    return open_at(df, t) & (age_days(df, t) <= config.ACTIVE_MAX_AGE_DAYS)


def stuck_at(df: pd.DataFrame, t: pd.Timestamp) -> pd.Series:
    return open_at(df, t) & (age_days(df, t) > config.ACTIVE_MAX_AGE_DAYS)


def counted_completions(df: pd.DataFrame) -> pd.DataFrame:
    """Completions that count towards throughput: administrative closures are not repairs."""
    return df.loc[df["completed_at"].notna() & ~df["is_admin_closure"]]


def four_week_window(t: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    """[start, end) of the four full Monday-to-Sunday weeks ending on or before t."""
    monday = (t.normalize() - pd.Timedelta(days=t.weekday()))
    end = monday + WEEK if t >= monday + WEEK - pd.Timedelta(seconds=1) else monday
    return end - 4 * WEEK, end


def weeks_to_clear(df: pd.DataFrame, t: pd.Timestamp, by: str | list[str],
                   field_crew: set[str] = frozenset()) -> pd.DataFrame:
    """Active open work ÷ average weekly completions over the four full weeks ending at t.

    The flag is raised only for groups in field_crew: contractors are not called for
    administrative sections, however slowly they clear their work.
    """
    start, end = four_week_window(t)
    done = counted_completions(df)
    in_window = done.loc[(done["completed_at"] >= start) & (done["completed_at"] < end)]
    table = pd.DataFrame({
        "active": df.loc[active_at(df, t)].groupby(by).size(),
        "avg_weekly_completions": in_window.groupby(by).size() / 4,
    }).fillna(0)
    table["active"] = table["active"].astype(int)
    enough = table["avg_weekly_completions"] >= config.MIN_WEEKLY_COMPLETIONS
    table["weeks_to_clear"] = np.where(enough, table["active"] / table["avg_weekly_completions"], np.nan)
    table["field_crew"] = table.index.isin(list(field_crew))
    table["flag"] = table["field_crew"] & (table["weeks_to_clear"] > config.DEFAULT_THRESHOLD_WEEKS)
    return table.sort_values("weeks_to_clear", ascending=False)


def suburb_rank(df: pd.DataFrame, t: pd.Timestamp, sections: list[str], top: int = 10) -> dict:
    """Inside each flagged section, suburbs by active open work, highest first.

    Requests with no suburb are not ranked: no contractor can be sent to them. Their active count
    is reported beside the ranking instead (unknown_suburb_active).
    """
    table = (
        weeks_to_clear(df, t, ["section", "official_suburb"])
        .drop(columns=["field_crew", "flag"]).reset_index()
    )
    known = table.loc[table["official_suburb"].ne(config.UNKNOWN_SUBURB)]
    return {
        section: _records(
            known.loc[known["section"].eq(section)]
            .sort_values(["active", "official_suburb"], ascending=[False, True])
            .drop(columns="section").head(top).set_index("official_suburb")
        )
        for section in sections
    }


def unknown_suburb_active(df: pd.DataFrame, t: pd.Timestamp, sections: list[str]) -> dict[str, int]:
    """Active open work with no suburb, per flagged section: shown beside the suburb rank."""
    unknown = df.loc[active_at(df, t) & df["official_suburb"].eq(config.UNKNOWN_SUBURB)]
    counts = unknown.groupby("section").size()
    return {section: int(counts.get(section, 0)) for section in sections}


def age_buckets(df: pd.DataFrame, t: pd.Timestamp) -> dict[str, int]:
    ages = age_days(df.loc[open_at(df, t)], t)
    return {
        label: int(ages.between(low, high if high is not None else np.inf).sum())
        for low, high, label in config.AGE_BUCKETS
    }


def durations(df: pd.DataFrame, by: str) -> pd.DataFrame:
    days = counted_completions(df).groupby(by)["days_to_complete"]
    return pd.DataFrame({
        "completed": days.size(),
        "median_days": days.median(),
        "p90_days": days.quantile(0.9),  # linear interpolation = DAX PERCENTILEX.INC
    }).sort_values("completed", ascending=False)


def weekly_flow(df: pd.DataFrame) -> pd.DataFrame:
    requests_in = df.groupby(week_start(df["created_at"])).size()
    done = counted_completions(df)
    completions = done.groupby(week_start(done["completed_at"])).size()
    flow = pd.DataFrame({"requests_in": requests_in, "completions": completions}).fillna(0).astype(int)
    flow = flow.loc[flow.index.year == 2020]
    flow["net_change"] = flow["requests_in"] - flow["completions"]
    return flow


def compute(df: pd.DataFrame, scoped_rows: int, quarantine: pd.DataFrame) -> dict:
    located = df["is_located"]
    reference = {
        "transparency": {
            "in_scope_rows": scoped_rows,
            "clean_rows": len(df),
            "quarantined_rows": len(quarantine),
            "quarantined_by_reason": quarantine["reason_code"].value_counts().to_dict(),
            "reconciles": scoped_rows == len(df) + len(quarantine),
            "admin_closure_rows": int(df["is_admin_closure"].sum()),
            "admin_closure_share": df["is_admin_closure"].mean(),
            "likely_repeat_rows": int(df["is_likely_repeat"].sum()),
            "likely_repeat_share_of_located": df.loc[located, "is_likely_repeat"].mean(),
            "unlocated_rows": int((~located).sum()),
            "unlocated_share": (~located).mean(),
        },
        "durations_by_section": _records(durations(df, "section")),
        "durations_by_code_group": _records(durations(df, "code_group")),
        "weekly_flow": _records(weekly_flow(df), index_name="week_start"),
        "as_at": {},
    }
    for date in config.REFERENCE_DATES:
        t = as_at_end(date)
        open_now = df.loc[open_at(df, t)]
        by_hex = open_now.loc[open_now["is_located"]].groupby("h3_level8_index").size()
        by_section = weeks_to_clear(df, t, "section", config.FIELD_CREW_SECTIONS)
        flagged = by_section.index[by_section["flag"]].tolist()
        reference["as_at"][date] = {
            "open": len(open_now),
            "active": int(active_at(df, t).sum()),
            "stuck": int(stuck_at(df, t).sum()),
            "open_by_section": open_now.groupby("section").size().to_dict(),
            "stuck_by_section": df.loc[stuck_at(df, t)].groupby("section").size().to_dict(),
            "age_buckets": age_buckets(df, t),
            "hexagons_with_open_work": len(by_hex),
            "top_hexagons": by_hex.sort_values(ascending=False).head(10).to_dict(),
            "unlocated_open": int((~open_now["is_located"]).sum()),
            "weeks_to_clear_by_section": _records(by_section),
            "flagged_sections": flagged,
            "suburb_rank_in_flagged_sections": suburb_rank(df, t, flagged),
            "unknown_suburb_active_in_flagged_sections": unknown_suburb_active(df, t, flagged),
        }
    return reference


def map_dataset(df: pd.DataFrame, dim_hex: pd.DataFrame, t: pd.Timestamp) -> list[dict]:
    """The rows the Deneb Operations Map receives on date t: one per hexagon, with its measures."""
    open_now = df.loc[open_at(df, t)].assign(age=lambda x: age_days(x, t))
    per_hex = open_now.groupby("h3_level8_index").agg(
        map_open=("age", "size"),
        map_stuck=("age", lambda a: int((a > config.ACTIVE_MAX_AGE_DAYS).sum())),
        map_oldest_days=("age", "max"),
    )
    rows = dim_hex[["hex_id", "area", "coords"]].merge(
        per_hex, left_on="hex_id", right_index=True, how="left"
    )
    rows = rows.loc[rows["coords"].notna()].rename(columns={
        "map_open": "Map Open", "map_stuck": "Map Stuck", "map_oldest_days": "Map Oldest Days",
    })
    rows["Map Open"] = rows["Map Open"].fillna(0).astype(int)
    return json.loads(rows.to_json(orient="records"))


def write(reference: dict | list, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reference, f, indent=1, default=_json_default)


def _records(table: pd.DataFrame, index_name: str | None = None) -> list[dict]:
    table = table.reset_index()
    if index_name:
        table = table.rename(columns={table.columns[0]: index_name})
    return json.loads(table.to_json(orient="records", date_format="iso", double_precision=6))


def _json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else round(float(value), 6)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    raise TypeError(f"Not JSON serialisable: {type(value)}")
