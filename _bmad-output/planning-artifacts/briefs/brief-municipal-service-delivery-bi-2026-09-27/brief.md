---
title: "Product Brief: Municipal Service Delivery BI"
status: final
created: 2026-09-27
updated: 2026-09-27
---

# Product Brief: Municipal Service Delivery BI

## Executive Summary

A Power BI dashboard that answers two questions each week for the City of Cape Town's Director
of Water and Sanitation. Can field crews clear the open workload in time, or must contractors be
called in? Which section, area or fault type is holding work up? Its centrepiece is the
**Operations Map**, which highlights every location with open maintenance work on a date the
Director chooses.

It is built on the 351,148 field-work requests the City published for 2020, cleaned through a
documented pipeline in which every removed row is accounted for. That year, open field work less
than 90 days old rose by 45% between the end of March and the end of December. In the sewer
section, the median job took 2.5 days, but the slowest tenth took more than 144 days. Those two
facts are the case for the dashboard.

This is a portfolio project: a working demonstration on historical data, designed so the same
model could point at a live feed.

## The Problem

The Director has a finite pool of field crews and a backlog that grows unevenly. Two decisions
recur:

- **When to call in contractors.** If they are called too late, the backlog ages and residents
  wait months. If they are called too early, budget goes where crews could have coped. [ASSUMPTION — confirm with a
  practitioner] Today the call is made from backlog totals by department, which show how much is
  open but not where it is building up, or whether crews are gaining or losing ground.
- **Where operations are bottlenecked.** A median of a few days hides a tail of jobs that stay
  open for months. Totals and averages do not show which section, area or fault type owns that
  tail.

## The Solution

Three pages, one question each.

1. **Director overview: are we keeping up?** Open work over time, requests in against requests
   completed per week, and *weeks to clear* per section and area. A contractor flag is raised
   when weeks to clear exceeds a threshold the Director sets.
2. **Operations Map: where is open work?** Every location with an open request on a chosen date,
   highlighted on a map of the City.
3. **Bottlenecks: what is holding work up?** Median and 90th-percentile time to complete by
   section, area and fault type, and the age of what is still open.

The addendum holds the *weeks to clear* formula, the cleaning rules with row counts and the
Operations Map's time model.

## What Makes This Different

- **Real data, cleaned in the open.** Every cleaning rule has a reason and a count, and raw rows
  reconcile to clean plus quarantined rows.
- **A decision rule, not only charts.** The contractor flag is a stated rule with an adjustable
  threshold.
- **Built as code.** The semantic model is version-controlled as PBIP/TMDL, and its measures are
  tested, through the Power BI Authoring MCP server, against independently computed values.

## Who This Serves

**Primary: the Director of Water and Sanitation.** Accountable for the metro's open water and
sewer requests, with a finite pool of field crews spread across depots. Once a week they decide
whether to call in contractors and where operations need intervention.

**Not served in v1.0:** residents, ward councillors, call-centre agents, district
managers.

## Success Criteria

- [ASSUMPTION — proposed] In under five minutes, the Director can answer both weekly questions
  from the dashboard alone.
- Every measure shown matches an independently computed value in automated tests.
- Raw field-work rows equal clean plus quarantined rows, and the dashboard shows the reconciliation.
- Any number on screen can be traced to a cleaning rule, a measure definition and a test.
- v1.0 is publicly viewable by 4 October 2026: repository, screenshots and a short video
  walkthrough. (No Power BI Service account is available, so there is no live published link.)

## Scope

**In for v1.0:** Water and Sanitation field work created in 2020: sewer, water and water
management device requests, including those in informal settlements; the three pages; the cleaning pipeline with
quarantine; the contractor flag.

**Out for v1.0:** billing and meter queries; other directorates; crew capacity and contractor cost
(not in the data); bottlenecks between process steps (no status history); service-standard
targets; row-level security; live data; financial data.

## Known Limitations

- **One year, and an unusual one.** The data covers requests created in 2020. The COVID-19 hard
  lockdown halved request volumes in April.
- **Backlog before 2020 is missing.** Requests created in 2019 and still open in 2020 are not in the
  data, so total open work is understated early in the year. Comparisons over time use work less
  than 90 days old, which is complete from 31 March 2020.
- **Open is not the same as in progress.** Only creation and completion times are published, so
  the dashboard cannot show whether a crew is on site.
- **Crew capacity is inferred.** Completions per week stand in for what crews can deliver.
- **9% of requests have no location.** They count in totals but cannot appear on the map.
- **Cape Town is not typical.** It publishes this data because it is well run; struggling
  municipalities may not have data of this quality.

## Roadmap

| Version | Adds |
|---|---|
| v1.0 | The three pages above |
| v1.1 | Play-through animation on the Operations Map; full PRD |
| v1.2 | Service standards: targets held as data, working-day calendar, missed targets on the map |
| v1.3 | Repeat faults: same area and fault type within 30 days, as a pipe-replacement signal |
| v1.4 | Maintenance spending against National Treasury's norm of 8% of asset value, using Municipal Money (Treasury's open municipal finance data) |
