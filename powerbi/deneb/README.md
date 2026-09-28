# Operations Map (Deneb)

`operations-map.vl.json` draws every H3 hexagon of the City of Cape Town and colours each one by
the number of field-work requests open on the date chosen in the as-at slicer. Hexagons with no
open work stay grey, so the outline of the municipality is always visible.

![Render test: 31 March and 31 December 2020](../../docs/images/operations-map-render-test.png)

*Render test outside Power BI, using the same Vega-Lite grammar Deneb runs. The December map shows
more open work partly because requests created before 2020 are missing from the data, which
hides the backlog carried into early 2020.*

## Set-up in Power BI Desktop

1. **Load the tables.** Run `uv run python -m pipeline.run`, then *Get data → Parquet* for each
   file in `data/processed/`.
2. **Relate them** in Model view: `fact_request` to `dim_section`, `dim_fault_type`, `dim_suburb`
   and `dim_hex` on their keys; `created_date` to `dim_date[date]` (active) and `completed_date` to
   `dim_date[date]` (inactive). **Leave `as_at` unrelated.** A relationship would make the slicer
   select requests *created* on the chosen day instead of requests *open* on it.
3. **Add a single-select slicer** on `as_at[as_at_date]`.
4. **Add Deneb** (*Get more visuals → Deneb*) and drag in, in this order:
   `dim_hex[hex_id]`, `dim_hex[coords]`, `dim_hex[area]`, then the measures `Map Open`,
   `Map Stuck` and `Map Oldest Days`. The field names must match exactly: the spec refers to them
   by name.
5. **Paste the spec.** *Edit → Vega-Lite → Empty*, paste `operations-map.vl.json` into the
   Specification pane and select *Apply*. If hovering shows no tooltip, turn tooltips on in
   Deneb's settings.

## Test the visual before writing the real measures

Prove the map renders first, with a throwaway measure that ignores the date:

```
Map Open = COUNTROWS ( fact_request ) + 0
```

`+ 0` makes hexagons with no requests return 0 instead of blank. Power BI drops rows where every
measure is blank, and the grey outline of the City would disappear with them.

Once the map draws, replace it with the real definition from the spec's `measures.md`: requests
open at the end of the chosen day, per hexagon, 0 where none. Write `Open Now` yourself and build
`Map Open`, `Map Stuck` and `Map Oldest Days` on it.

## Check the numbers

The pipeline writes the exact rows this visual should receive for four test dates to
`data/processed/map/<date>.json`, and the expected totals to `reference_values.json`
(`hexagons_with_open_work`, `top_hexagons`). On 31 December 2020, 1,390 hexagons should be
highlighted.

To re-render outside Power BI after changing the spec:

```
npm install --no-save vega@5 vega-lite@5
node powerbi/deneb/render-test.mjs data/processed/map/2020-12-31.json map.svg
```

## What the map cannot show

- **Unlocated requests.** 9% of requests have no location. Put a card beside the map with the
  unlocated count for the chosen date. For informal-settlement work the gap is far larger: on
  31 December 2020, 34% of that section's open work had no location, against 2–3% for the
  reticulation sections. The map under-shows exactly the areas where service is weakest.
- **Backlog from before 2020.** It is not in the published data.
- **Crews.** A highlighted hexagon has open requests; the data cannot say whether anyone is on site.

## Fallback

If Deneb misbehaves in Desktop, use a built-in map with `dim_hex[centroid_lat]` and
`dim_hex[centroid_lon]`, bubbles sized by `Map Open`.
