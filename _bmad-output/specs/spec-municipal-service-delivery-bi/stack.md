# Stack

| Layer | Choice | Reason |
|---|---|---|
| Source | `sr_hex.csv.gz` and `city-hex-polygons-8.geojson` from the City's public bucket `cct-ds-code-challenge-input-data` (af-south-1) | Only reachable copy of the published service requests; the hexagon polygons come from the same publisher |
| Pipeline | Python 3.12, pandas, pyarrow, run with `uv` | Runs identically on Windows and Linux; no environment setup beyond `uv` |
| Storage | Parquet files in `data/processed/` (not committed) | Typed, compact, read natively by Power BI's Parquet connector |
| Tests | pytest over the pipeline; `reference_values.json` as the expected values for DAX tests | One source of truth for both test layers |
| Model | Power BI Desktop, saved as PBIP with TMDL in `powerbi/` | Text files diff in git and can be edited by the Power BI Authoring MCP server |
| Model tests | Power BI Authoring MCP server `@microsoft/powerbi-modeling-mcp@1.0.0` (pinned), connected to Desktop; DAX results compared with `reference_values.json` | Automated proof that on-screen numbers match the pipeline |
| Map | Deneb (Vega-Lite) with hexagon polygons; fallback: bubble map at hexagon centres | Decided by the Day 3 test |
| Delivery | Git tags per release, `CHANGELOG.md`, screenshots and a video walkthrough in the README | No Power BI Service account |
