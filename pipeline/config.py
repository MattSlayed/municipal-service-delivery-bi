"""Pipeline settings: source files, scope and cleaning thresholds.

Every value here is referenced by the v1.0 spec
(_bmad-output/specs/spec-municipal-service-delivery-bi/).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DQ_REPORT = ROOT / "docs" / "data-quality-report.md"

BUCKET = "https://cct-ds-code-challenge-input-data.s3.af-south-1.amazonaws.com"
REQUESTS_FILE = "sr_hex.csv.gz"
HEXAGONS_FILE = "city-hex-polygons-8.geojson"
SOURCES = {
    REQUESTS_FILE: f"{BUCKET}/{REQUESTS_FILE}",
    HEXAGONS_FILE: f"{BUCKET}/{HEXAGONS_FILE}",
}

TIMEZONE = "Africa/Johannesburg"

DIRECTORATE = "WATER AND SANITATION"
FIELD_CODE_GROUPS = {
    "SEWER",
    "WATER",
    "WATER MANAGEMENT DEVICE",
    "SEWER - INFORMAL SETTLEMENTS",
    "WATER  - INFORMAL SETTLEMENTS",  # two spaces, as published
}

UNLOCATED_HEX = "0"
ADMIN_CLOSURE_SECONDS = 300
MIN_WEEKLY_COMPLETIONS = 5
DEFAULT_THRESHOLD_WEEKS = 2.0
REFERENCE_DATES = ["2020-03-31", "2020-06-30", "2020-09-30", "2020-12-31"]
AGE_BUCKETS = [(0, 7, "0-7 days"), (8, 30, "8-30 days"), (31, 90, "31-90 days"),
               (91, 365, "91-365 days"), (366, None, "Over 365 days")]
