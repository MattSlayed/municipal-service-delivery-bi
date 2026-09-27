# Addendum: Product Brief — Municipal Service Delivery BI

Detail that belongs downstream (PRD, UX, architecture) rather than in the brief.

## Operations map (the "twin")

**Definition agreed with Matthew:** a map of the municipality where a location is highlighted
while a maintenance task there is running. No live integration with municipal systems.

**Notes for PRD and architecture:**

- **What "running" can mean depends on the data.** If the published records carry only creation
  and completion timestamps, "running" means *open*: created and not yet completed. It cannot mean
  "crew on site". Verify against the dataset before the PRD fixes the definition.
- **"Whenever" needs a time model.** The data is historical, so "whenever a task is running"
  becomes "at a chosen point in time". A task is open at time *t* when it was created at or
  before *t* and was not completed by *t*. A date-time slider or play axis over the map shows the
  city's open work changing, without streaming infrastructure.
- **Map resolution is set by the published geography**: point, H3 hexagon, suburb or ward. The
  City's data-science challenge uses H3 level-8 hexagons; the portal dataset's geography is
  unverified.
- **It shows work by area, not assets.** The water pipe network is unlikely to be published, so
  this is not an asset or hydraulic twin.
- **Visual options to prototype early:** Deneb (Vega-Lite) with GeoJSON shapes, or a custom map
  visual. Custom maps are where Power BI resists most.

## Contractor flag (agreed)

- **Weeks to clear** = open requests ÷ average weekly completions over the previous four weeks,
  calculated per section and per area.
- **Flag** when weeks to clear exceeds a threshold the Director sets with a slider. Default: 2 weeks.
- Completions per week stand in for crew capacity, which is not in the data.

## Cleaning rules (field-work scope, 351,148 rows)

Principle: remove only what is provably invalid, and quarantine it with a reason code so that
raw rows = clean rows + quarantined rows. Flag what is doubtful; never delete it silently.

| Rule | Rows | Action |
|---|---|---|
| Exact duplicate records or notification numbers | 0 | Remove. None found; the check stays as a guard |
| Completed before created | 478 | Quarantine, reason `NEGATIVE_DURATION` |
| Closed within 5 minutes of creation | 5,363 | **Decision pending.** Likely administrative closures (1,868 are burst pipes, which cannot be repaired in 5 minutes). Proposed: keep in request counts, exclude from durations and completions-per-week, flag `ADMIN_CLOSURE` |
| No location | 31,761 | Keep. Excluded from the map only |
| No section | 35,939 | Keep as "Unassigned section" |
| Same fault type, hexagon and day (likely repeat reports) | 70,296 | Keep. Flag `LIKELY_REPEAT`; show the share (agreed with Matthew) |
| Open or took more than 365 days | 3,117 | Keep. This tail is the bottleneck finding |
