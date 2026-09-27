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
