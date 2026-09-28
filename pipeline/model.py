"""Build the star schema described in the spec's data-model.md."""

import json

import pandas as pd

from . import config

UNASSIGNED = "Unassigned"
UNKNOWN_SUBURB = "Unknown suburb"


def prepare_labels(clean: pd.DataFrame) -> pd.DataFrame:
    """Fill missing descriptive values with explicit labels, so no request drops out of a visual."""
    df = clean.copy()
    for column in ["department", "branch", "section"]:
        df[column] = df[column].fillna(UNASSIGNED)
    df["official_suburb"] = df["official_suburb"].fillna(UNKNOWN_SUBURB)
    df["is_informal_settlement"] = df["code_group"].str.contains("INFORMAL SETTLEMENTS")
    return df


def build(df: pd.DataFrame, hexagons_path) -> dict[str, pd.DataFrame]:
    dim_section = _dimension(df, ["department", "branch", "section"], "section_key")
    dim_fault_type = _dimension(df, ["code_group", "code", "is_informal_settlement"], "fault_type_key")
    dim_suburb = _dimension(df.rename(columns={"official_suburb": "suburb"}), ["suburb"], "suburb_key")
    dim_hex = _hex_dimension(df, hexagons_path)

    fact = (
        df.rename(columns={"official_suburb": "suburb", "h3_level8_index": "hex_id"})
        .merge(dim_section, on=["department", "branch", "section"], validate="many_to_one")
        .merge(dim_fault_type, on=["code_group", "code", "is_informal_settlement"], validate="many_to_one")
        .merge(dim_suburb, on="suburb", validate="many_to_one")
        .merge(dim_hex[["hex_key", "hex_id"]], on="hex_id", validate="many_to_one")
    )
    fact = fact.assign(
        request_id=fact["notification_number"],
        created_date=fact["created_at"].dt.date,
        completed_date=fact["completed_at"].dt.date,
    )[[
        "request_id", "created_at", "completed_at", "created_date", "completed_date",
        "section_key", "fault_type_key", "suburb_key", "hex_key", "days_to_complete",
        "is_admin_closure", "is_likely_repeat", "is_located",
    ]].sort_values("created_at", kind="stable").reset_index(drop=True)

    last_day = max(df["created_at"].max(), df["completed_at"].max()).normalize()
    return {
        "fact_request": fact,
        "dim_date": _date_dimension(pd.Timestamp("2020-01-01"), last_day),
        "dim_section": dim_section,
        "dim_fault_type": dim_fault_type,
        "dim_suburb": dim_suburb,
        "dim_hex": dim_hex,
        "as_at": _as_at(),
    }


def _dimension(df: pd.DataFrame, columns: list[str], key: str) -> pd.DataFrame:
    dim = df[columns].drop_duplicates().sort_values(columns).reset_index(drop=True)
    dim.insert(0, key, range(1, len(dim) + 1))
    return dim


def _hex_dimension(df: pd.DataFrame, hexagons_path) -> pd.DataFrame:
    """Every hexagon of the City (so the map draws the whole municipality), plus any hexagon a
    request uses that the polygon file lacks, plus the "0" placeholder for unlocated requests."""
    with open(hexagons_path, encoding="utf-8") as f:
        features = json.load(f)["features"]
    polygons = pd.DataFrame({
        "hex_id": [ft["properties"]["index"] for ft in features],
        "centroid_lat": [ft["properties"]["centroid_lat"] for ft in features],
        "centroid_lon": [ft["properties"]["centroid_lon"] for ft in features],
        "coords": [_map_coords(ft["geometry"]["coordinates"][0]) for ft in features],
    })
    used = pd.DataFrame({"hex_id": df["h3_level8_index"].unique()})
    dim = (
        polygons.merge(used, on="hex_id", how="outer", validate="one_to_one")
        .sort_values("hex_id", ignore_index=True)
    )
    dim["hex_label"] = dim["hex_id"].where(dim["hex_id"].ne(config.UNLOCATED_HEX), "Unlocated")
    dim["area"] = dim["hex_id"].map(_main_suburb(df))
    dim.insert(0, "hex_key", range(1, len(dim) + 1))
    return dim


def _main_suburb(df: pd.DataFrame) -> pd.Series:
    """The suburb most requests in each hexagon name, so the map tooltip reads as a place."""
    located = df.loc[df["h3_level8_index"].ne(config.UNLOCATED_HEX)]
    counts = located.groupby(["h3_level8_index", "official_suburb"]).size().reset_index(name="n")
    return (
        counts.sort_values(["h3_level8_index", "n", "official_suburb"], ascending=[True, False, True])
        .drop_duplicates("h3_level8_index")
        .set_index("h3_level8_index")["official_suburb"]
    )


def _map_coords(ring: list[list[float]]) -> str:
    """Flatten a polygon ring to "lon,lat,lon,lat,..." wound clockwise.

    Vega draws with d3-geo, which treats an anticlockwise ring as "the whole globe except this
    hexagon" and floods the map. The shoelace sum is positive for anticlockwise rings.
    """
    shoelace = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:]))
    if shoelace > 0:
        ring = ring[::-1]
    return ",".join(f"{value:.{config.MAP_COORD_DECIMALS}f}" for point in ring for value in point)


def _date_dimension(first: pd.Timestamp, last: pd.Timestamp) -> pd.DataFrame:
    days = pd.date_range(first, last, freq="D")
    return pd.DataFrame({
        "date": days.date,
        "year": days.year,
        "quarter": [f"{d.year} Q{d.quarter}" for d in days],
        "month_start": days.to_period("M").start_time.date,
        "month_name": days.strftime("%b %Y"),
        "week_start": (days - pd.to_timedelta(days.weekday, unit="D")).date,
        "day_of_week": days.strftime("%a"),
        "is_2020": days.year == 2020,
    })


def _as_at() -> pd.DataFrame:
    days = pd.date_range("2020-01-01", "2020-12-31", freq="D")
    return pd.DataFrame({
        "as_at_date": days.date,
        "as_at_end": days + pd.Timedelta(days=1) - pd.Timedelta(seconds=1),
    })
