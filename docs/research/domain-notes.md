# Domain notes

Seed input for the Analysis phase, collected before the product brief. These are inputs, not
requirements. Items marked **[verify]** have not been checked against a primary source.

## Governance context

- Municipal finances are governed by the Municipal Finance Management Act 56 of 2003 (MFMA).
- South Africa has 257 municipalities: 8 metropolitan, 205 local and 44 district.
- Councillors represent wards, and ward boundaries are re-delimited before each local government
  election. Any ward dimension needs versioning, or history will be reported against boundaries
  that did not exist at the time. **[verify]** The next local government elections, and the
  delimitation that goes with them, are due around late 2026 or early 2027.

## Service requests

- Typical categories: water and sanitation, electricity, roads and stormwater, refuse removal,
  parks, by-law enforcement.
- Typical intake channels: walk-in, call centre, email, mobile app, WhatsApp. The same fault is
  often reported several times across channels, so deduplication is a real data problem, not a
  nice-to-have.
- **[verify]** Turnaround-time commitments come from each municipality's own service standards or
  service delivery charter. There is no single national SLA table, so the model must hold SLA
  targets as data, not as constants in DAX.

## Public data sources

| Source | Use | Notes |
|---|---|---|
| City of Cape Town Open Data Portal ([odp-cctegis.opendata.arcgis.com](https://odp-cctegis.opendata.arcgis.com/)) | Real service-request records; ward, subcouncil and suburb boundaries | The City's own [data-science code challenge](https://github.com/cityofcapetown/ds_code_challenge) uses ~941k service requests with H3 level-8 hexagons, and states that notification and reference numbers are removed before publication. **[verify]** Date range, refresh cadence, fields and licence terms of the portal dataset |
| Municipal Money, National Treasury ([municipalmoney.gov.za](https://municipalmoney.gov.za), API at [municipaldata.treasury.gov.za](https://municipaldata.treasury.gov.za)) | Budgets, spending, repairs and maintenance, unauthorised/irregular/fruitless expenditure, audit outcomes | Real data for the financial-health page |
| MFMA Circular 71 | Financial ratio norms | Repairs and maintenance as % of property, plant and equipment: norm of 8% |
| Stats SA, Census 2022 | Households and access to services by municipality and ward | Denominators for per-household rates |
| Public Holidays Act 36 of 1994 | Working-day calendar | A holiday falling on a Sunday moves to the Monday. Needed for turnaround times in working days |

## Privacy

- Service requests carry names, phone numbers and addresses: personal information under the
  Protection of Personal Information Act 4 of 2013 (POPIA).
- This project uses only data a municipality has already published as open data, in the form it
  was published. No attempt is made to re-identify residents or to enrich records with personal
  information from elsewhere.
- The Power BI Authoring MCP server sends model metadata and query results to the AI provider.
  That is acceptable for published open data and would not be for a production model holding
  citizen data.

## Open questions for the product brief

1. Who is the primary user: the municipal manager, a department director, a ward councillor, or a
   call-centre supervisor? What decision does each make that this dashboard should change?
2. Which municipality? Real data was chosen, so the choice depends on who publishes
   service-request records. Cape Town is confirmed; other metros not yet checked.
3. What counts as "resolved": closed by the call centre, closed by the field team, or confirmed by
   the resident?
4. Which service categories are in scope for the first release?
5. What refresh cadence would a real municipality need: daily, hourly, near real time?
