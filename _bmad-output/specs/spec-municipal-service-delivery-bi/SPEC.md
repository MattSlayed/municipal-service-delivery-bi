---
id: SPEC-municipal-service-delivery-bi
companions:
  - measures.md
  - data-model.md
  - stack.md
  - ../../planning-artifacts/briefs/brief-municipal-service-delivery-bi-2026-09-27/addendum.md
  - ../../../docs/research/data-profile.md
sources:
  - ../../planning-artifacts/briefs/brief-municipal-service-delivery-bi-2026-09-27/brief.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Municipal Service Delivery BI — v1.0

## Why

**Pain to solve, under a deadline.** The City of Cape Town's Director of Water and Sanitation must
decide each week whether field crews can clear open work or contractors must be called in, and
where operations are held up. In 2020, open field work less than 90 days old rose by 45% between
the end of March and the end of December; in the sewer section the median job took 2.5 days, but
the slowest tenth took more than 144. Department totals do
not show where work is building up or which jobs are stuck. The dashboard must also stand as
public portfolio evidence by 4 October 2026.

## Capabilities

- **CAP-1** Clean, reconciled data
  - **intent:** The City's published field-work requests become analysis-ready data in which every excluded row is accounted for.
  - **success:** Raw in-scope rows = clean rows + quarantined rows, by reason code, in an automated test; flag counts are reported by the pipeline.
- **CAP-2** Keeping-up view
  - **intent:** The Director sees whether crews are keeping up: open work over time, and requests in against completions per week.
  - **success:** Open-at-date and weekly counts in Power BI equal the pipeline's reference values for the test dates in `measures.md`.
- **CAP-3** Contractor flag
  - **intent:** The Director sees weeks to clear per section and suburb, flagged where it exceeds a threshold they set.
  - **success:** For a given as-at date and threshold, the flagged set in Power BI equals the reference computation; the threshold is adjustable, default 2 weeks.
- **CAP-4** Operations Map
  - **intent:** The Director sees every location with open field work at a chosen date, highlighted on a map of the City.
  - **success:** Highlighted hexagons and their open counts at a chosen date equal the reference; unlocated open requests are reported as a share, not mapped.
- **CAP-5** Bottlenecks
  - **intent:** The Director sees which section, suburb and fault type hold work up.
  - **success:** Median and 90th-percentile days to complete, and ageing buckets of open work, equal the reference values per section.
- **CAP-6** Data transparency
  - **intent:** Every viewer sees what the data can and cannot show.
  - **success:** Reconciliation, likely-repeat share, admin-closure share, unlocated share and the 2020/COVID caveat are visible on the dashboard and equal pipeline counts.

## Constraints

- Only creation and completion timestamps exist. "Open at *t*" means created at or before *t* and not completed by *t*. Bottlenecks between process steps cannot be shown.
- Scope: directorate `WATER AND SANITATION`; code groups `SEWER`, `WATER`, `WATER MANAGEMENT DEVICE`, `SEWER - INFORMAL SETTLEMENTS`, `WATER  - INFORMAL SETTLEMENTS` (two spaces, as in the source).
- Cleaning quarantines only provably invalid rows, with a reason code, and flags doubtful rows. Nothing is deleted silently.
- `ADMIN_CLOSURE` rows count as requests but are excluded from durations and from completions per week.
- Durations are reported as median and 90th percentile, never as a mean.
- All timestamps are in SAST (Africa/Johannesburg). Weeks start on Monday.
- Built in Power BI Desktop on Windows; the model is saved as PBIP/TMDL in git. No Power BI Service account: no publish-to-web, scheduled refresh or row-level security.
- Raw and processed data are not committed; the pipeline regenerates them and runs on Windows and Linux.
- The measures carrying the core logic (open at *t*, weeks to clear, contractor flag) are written by hand by Matthew. Agents may write the rest and the tests.
- Budget: about 20–24 hours before 4 October 2026.
- Requests created before 2020 are absent, so total open work is understated early in 2020. Comparisons over time use work less than 90 days old, complete from 31 March 2020.

## Non-goals

- Billing, meter and account queries; directorates other than Water and Sanitation.
- Crew capacity, crew location and contractor cost (not in the data).
- Bottlenecks between process steps.
- Service-standard targets and compliance (v1.2); play-through animation (v1.1); repeat-fault analysis (v1.3); financial data (v1.4).
- Removing likely repeat reports.
- Live data, publish-to-web and row-level security.
- Audiences other than the Director: residents, ward councillors, call-centre agents, district managers.

## Success signal

In a recorded walkthrough, the Director's two questions — "do we call in contractors this week, and
where?" and "what is holding work up?" — are answered from the dashboard in under five minutes, and
every number shown passes its automated comparison with the pipeline's reference values.

## Assumptions

- Weeks to clear is calculated per official suburb; hexagons are used for the map only.
- Weeks to clear is left blank where average weekly completions are below 5, so small suburbs do not raise noise-driven flags.
- Duration measures are grouped by creation date.
- Requests closed within 5 minutes are administrative closures, not repairs.
- The City's published dataset may be reused in a public portfolio with attribution (unverified).
- The Director currently decides from department totals (unconfirmed with a practitioner).

## Open Questions

- Map rendering: Deneb with hexagon polygons, or the fallback of a bubble map at hexagon centres? Decided by the Day 3 test.
- Should the contractor flag list section × suburb combinations, or flag at section level with suburb drill-down?
