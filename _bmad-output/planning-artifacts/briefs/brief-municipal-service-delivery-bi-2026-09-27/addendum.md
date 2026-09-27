# Addendum: Product Brief — Municipal Service Delivery BI

Detail that belongs downstream (spec, PRD, UX, architecture) rather than in the brief.

## Cleaning rules (field-work scope, 351,148 rows)

Principle: remove only what is provably invalid, and quarantine it with a reason code so that
raw rows = clean rows + quarantined rows. Flag what is doubtful; never delete it silently.

| Rule | Rows | Action |
|---|---|---|
| Exact duplicate records or notification numbers | 0 | Remove. None found; the check stays as a guard |
| Completed before created | 478 | Quarantine, reason `NEGATIVE_DURATION` |
| Closed within 5 minutes of creation | 5,363 | Keep in request counts; exclude from durations and completions per week; flag `ADMIN_CLOSURE` (agreed with Matthew) |
| No location | 31,563 | Keep. Excluded from the map only |
| No section | 35,903 | Keep as "Unassigned" |
| Same fault type, hexagon and day (likely several reports of one fault) | 70,187 | Keep. Flag `LIKELY_REPEAT`; show the share (agreed with Matthew) |
| Open or took more than 365 days | 3,117 | Keep. This tail is the bottleneck finding |

Counts are after quarantine, from `docs/data-quality-report.md`.

**Why `ADMIN_CLOSURE`:** these are likely administrative closures, not repairs. 1,868 are burst
pipes, which cannot be repaired in 5 minutes. Counting them as completions would overstate crew
capacity and delay the contractor flag.

## Contractor flag (agreed)

- **Weeks to clear** = open requests ÷ average weekly completions over the previous four weeks,
  calculated per section and per area.
- Completions exclude `ADMIN_CLOSURE` rows (see Cleaning rules).
- **Flag** when weeks to clear exceeds a threshold the Director sets with a slider. Default: 2 weeks.
- Completions per week stand in for crew capacity, which is not in the data.

## Operations Map

**Definition agreed with Matthew:** a map of the municipality where a location is highlighted
while a maintenance task there is running. No live integration with municipal systems.

**Findings from the data (verified 27 September 2026):**

- **"Running" means open.** The published records carry only creation and completion timestamps,
  so a task is running from creation until completion. The data cannot show a crew on site.
- **"While a task is running" needs a time model.** The data is historical, so the map shows the
  city on a chosen date. A task is open on that date when it was created at or before the end of
  the day and not completed by then. A date slider or play axis shows open work changing without
  streaming infrastructure.
- **The map uses H3 level-8 hexagons.** Every located request carries one; 9% of requests have no
  location. "Area" for weeks to clear means official suburb.
- **It shows work by area, not assets.** The water pipe network is not published, so this is not
  an asset or hydraulic model.
- **Visual options to prototype early:** Deneb (Vega-Lite) with the City's hexagon polygons, or a
  custom map visual. Custom maps are where Power BI resists most.
