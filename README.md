# Municipal Service Delivery BI

A Power BI dashboard for the Director of Water and Sanitation in a South African metro: where
open work is building up, when to call in contractors, and where operations are bottlenecked.
Its centrepiece is an **Operations Map** that highlights every location with open maintenance work
at a chosen moment.

**Status: design phase. Nothing is built yet.** Requirements are being worked through with the
BMAD method. Planning artifacts land in `_bmad-output/planning-artifacts/` as each phase produces
them; this README is updated when something is real.

---

## Working hypothesis

To be tested in the product brief, not assumed:

> Municipalities receive service requests (water, electricity, roads, refuse) across walk-in, call
> centre, app and WhatsApp channels. The people accountable for resolving them — the municipal
> manager, department directors, ward councillors — lack a shared, trustworthy view of backlog,
> turnaround-time breaches and repeat faults, so resources go where complaints are loudest rather
> than where need is greatest.

## Approach

| Concern | Choice |
|---|---|
| Method | [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) v6.12.0 — Analysis → Planning → Solutioning → Implementation |
| Semantic model | Power BI Project (PBIP) with TMDL, version-controlled as text |
| Model authoring and testing | [Power BI Authoring MCP server](https://github.com/microsoft/powerbi-modeling-mcp) v1.0.0 — measures validated by DAX query, row-level security validated by role impersonation |
| Data | Real, published municipal data: City of Cape Town service requests (941,634 requests created in 2020; see [data profile](docs/research/data-profile.md)), financials from National Treasury's Municipal Money. |
| Releases | Versioned (v1.0, v1.1, ...), each tagged with a changelog and a short retrospective |

## Repository layout

```
_bmad/                  BMAD install (config, shared scripts)
.claude/skills/         BMAD agents and workflows for Claude Code
_bmad-output/           Planning and implementation artifacts produced by the BMAD phases
docs/research/          Domain notes and sources feeding the Analysis phase
```

Data, model and test folders are added once the Solutioning phase has decided their shape.

## Working on this repo

Requirements: Node.js 20.12+, [uv](https://docs.astral.sh/uv/), Claude Code. Power BI Desktop
(Windows) is needed from the Implementation phase onward.

Open the repo in Claude Code and run `/bmad-help` to see where the project is and what comes next.
