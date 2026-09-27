# Measures

Definitions every Power BI measure and every reference test must follow. Rules are stated in
plain language; the DAX is written against them. "Clean" means not quarantined.

## Time model

| Term | Definition |
|---|---|
| As-at time *t* | End of the day (23:59:59 SAST) chosen in a date table that has **no relationship** to the requests. A related table would filter requests to those created that day instead of those open |
| Week | Monday 00:00 to Sunday 23:59:59 SAST |
| Four weeks ending at *t* | The four full weeks ending on or before *t* |

## Workload

| Measure | Rule |
|---|---|
| Open at *t* | Clean requests with created ≤ *t* and (completed > *t* or never completed). Includes `LIKELY_REPEAT` and `ADMIN_CLOSURE` |
| Requests in (week) | Clean requests created in the week |
| Completions (week) | Clean requests completed in the week, excluding `ADMIN_CLOSURE` |
| Net change (week) | Requests in − Completions |

## Contractor flag

| Measure | Rule |
|---|---|
| Average weekly completions | Completions over the four weeks ending at *t*, ÷ 4 |
| Weeks to clear | Open at *t* ÷ Average weekly completions. Blank when average weekly completions < 5 |
| Threshold | What-if parameter, 0.5 to 8 weeks in steps of 0.5, default 2 |
| Contractor flag | Weeks to clear > Threshold |

Calculated per section and per official suburb.

## Bottlenecks

| Measure | Rule |
|---|---|
| Days to complete | (completed − created) in days, for completed clean requests excluding `ADMIN_CLOSURE`. Grouped by creation date |
| Median days to complete | Median of Days to complete |
| P90 days to complete | 90th percentile, inclusive linear interpolation (DAX `PERCENTILEX.INC`, pandas `quantile(0.9)`) |
| Age of open work at *t* | *t* − created, for requests open at *t*. Buckets: 0–7, 8–30, 31–90, 91–365, over 365 days |

## Data transparency

| Measure | Rule |
|---|---|
| Quarantined rows | Count by reason code |
| Reconciliation | In-scope raw rows = clean rows + quarantined rows |
| Likely-repeat share | `LIKELY_REPEAT` ÷ clean located requests |
| Admin-closure share | `ADMIN_CLOSURE` ÷ clean requests |
| Unlocated share | Clean requests without a hexagon ÷ clean requests; unlocated open requests at *t* shown beside the map |

## Reference test dates

Open at *t*, weekly flow, weeks to clear and flags are tested at 31 March, 30 June, 30 September and
31 December 2020. The pipeline writes the expected values to `reference_values.json`.
