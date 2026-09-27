# Municipal Service Delivery BI

A Power BI command centre for South African municipal service delivery: which service requests are
breaching turnaround times, where faults recur, and whether the maintenance budget matches the
backlog.

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
| Data | Real, openly published municipal data: service requests from a metro's open data portal (candidate: City of Cape Town), financials from National Treasury's Municipal Money, households from Census 2022. |
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
