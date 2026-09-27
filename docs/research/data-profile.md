# Data profile: City of Cape Town service requests

Profiled 2026-09-27 with `scripts/profile_service_requests.py` and `scripts/profile_field_work.py`.

## Source

- **File:** `sr_hex.csv.gz` (36.7 MB), published by the City of Cape Town's Data Science branch
  for its [public code challenge](https://github.com/cityofcapetown/ds_code_challenge):
  `https://cct-ds-code-challenge-input-data.s3.af-south-1.amazonaws.com/sr_hex.csv.gz`
- The Open Data Portal's own "Service requests" page was unreachable during profiling.
- Raw data is **not committed** to this repo. It is downloaded by script and attributed to the City.

## Shape

| Fact | Value |
|---|---|
| Rows | 941,634 service requests, all directorates |
| Created | 1 January – 31 December 2020 (SAST). **One year only** |
| Completed | Up to May 2022 |
| Timestamps | `creation_timestamp` and `completion_timestamp` only. No status history |
| Organisation | `directorate` → `department` → `branch` → `section` |
| Work type | `code_group` → `code`; `cause_code_group` → `cause_code` (86% empty) |
| Location | `latitude`, `longitude`, `official_suburb`, `h3_level8_index` |

## Water and Sanitation

- **422,834 requests** (45% of all), the largest directorate.
- **Field work** (code groups SEWER, WATER, WATER MANAGEMENT DEVICE and their informal-settlement
  variants): **351,148 requests**, 83% of the directorate. The rest are billing, meter and account
  queries, which are not crew work.
- 767 suburbs and 1,835 H3 level-8 hexagons. **9% of field-work requests have no location.**

### Time to complete (field work, days)

| Section | Requests | Median | 90th percentile |
|---|---|---|---|
| Reticulation WW Conveyance (sewer) | 124,275 | 2.4 | 143.8 |
| Reticulation Water Distribution | 88,233 | 6.7 | 71.1 |
| Meter Management | 82,989 | 3.3 | 15.2 |
| Informal Settlements: Operating and Maintenance | 14,581 | 8.0 | 88.2 |

| Code group | Median | 90th percentile |
|---|---|---|
| SEWER | 2.4 | 112.9 |
| SEWER – INFORMAL SETTLEMENTS | 7.0 | 84.9 |
| WATER | 5.1 | 65.1 |
| WATER – INFORMAL SETTLEMENTS | 9.2 | 112.1 |
| WATER MANAGEMENT DEVICE | 3.2 | 15.8 |

The gap between median and 90th percentile is large everywhere. Averages would mislead.

### Open field work at quarter-end, 2020

| As at | Open requests |
|---|---|
| 31 Mar | 14,504 |
| 30 Jun | 15,107 |
| 30 Sep | 22,853 |
| 31 Dec | 30,845 |

The open backlog roughly doubled in the second half of 2020.

### Monthly volume

Requests fell from 44,578 in January to 20,571 in April 2020 and recovered by October. This is
the COVID-19 hard lockdown (from 27 March 2020). 2020 is not a typical year, and the dashboard
must say so.

## Data quality

| Issue | Count | Handling (proposed) |
|---|---|---|
| Completed before created | 478 (field work) | Quarantine with reason code |
| Closed within 5 minutes of creation | 5,363 (field work) | Probably administrative closures, not repairs (1,868 are burst pipes). Decision pending |
| No location | 31,761 (9.0% of field work) | Keep in totals, exclude from the map, show the share |
| No section | 35,939 (10.2% of field work) | Keep as "Unassigned section" |
| Open or took more than 365 days | 3,117 (field work) | Keep: this tail is the bottleneck finding |
| Exact duplicate records or notification numbers | 0 | Nothing to remove; the check stays in the pipeline as a guard |
| Same fault type, same hexagon, same day | 70,296 (22.0% of located field work) | Likely repeat reports of one fault, but not certainly. Flag, do not delete. *Corrected: an earlier count of 94,255 wrongly grouped all unlocated requests into one hexagon* |
| Never completed | 145 (W&S) | Open at every point in time after creation |

## What this means for the design

- **"Running" means open**: created and not yet completed. The data cannot show a crew on site.
- **Open work can be reconstructed for any moment in 2020**, because almost every request has a
  completion time. The Operations Map's time slider works on this data.
- **Bottlenecks can be found by section, area and fault type**, where inflow outruns completions
  or the 90th percentile is extreme. Bottlenecks *between process steps* cannot be found: there is
  no step-level history.
