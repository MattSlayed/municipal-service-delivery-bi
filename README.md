# Municipal Service Delivery BI

A Power BI dashboard for the Director of Water and Sanitation in a South African metro: where
open work is building up, when to call in contractors, and where operations are bottlenecked.
Its centrepiece is an **Operations Map** that highlights every location with open maintenance work
at a chosen moment.

**Status: v1.0 in build.** The brief and spec are final and the data pipeline runs; the Power BI
model and report are next. Planning artifacts are in `_bmad-output/`; this README is updated when
something is real.

---

## Working hypothesis

To be tested in the product brief, not assumed:

> A Water and Sanitation Director with a finite pool of field crews has to decide, week by week,
> when internal capacity is not enough and contractors must be called in, and which part of
> operations is holding work up. Backlog totals by department do not show where open work is
> building up or which jobs are stuck, so the call comes late or lands in the wrong place.

## Approach

| Concern | Choice |
|---|---|
| Method | [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) v6.12.0 — Analysis → Planning → Solutioning → Implementation |
| Semantic model | Power BI Project (PBIP) with TMDL, version-controlled as text |
| Model authoring and testing | [Power BI Authoring MCP server](https://github.com/microsoft/powerbi-modeling-mcp) v1.0.0 — measures validated by DAX query against independently computed values |
| Data | Real, published municipal data: City of Cape Town service requests (941,634 requests created in 2020; see [data profile](docs/research/data-profile.md)), financials from National Treasury's Municipal Money. |
| Releases | Versioned (v1.0, v1.1, ...), each tagged with a changelog and a short retrospective |

## Repository layout

```
pipeline/               Download, scope, clean, star schema, reference values
tests/                  pytest: cleaning rules, measure definitions, reconciliation
docs/                   Research notes, data profile, generated data-quality report
_bmad-output/           Brief, spec and later implementation artifacts (BMAD)
_bmad/, .claude/skills/ BMAD install for Claude Code
```

## Working on this repo

Requirements: [uv](https://docs.astral.sh/uv/) and, for the model and report, Power BI Desktop
on Windows.

```
uv run python -m pipeline.run   # downloads the City's data, writes data/processed/*.parquet
uv run pytest                   # cleaning rules, measure definitions, reconciliation
```

The pipeline takes about 20 seconds after the first download. Source data is published by the
City of Cape Town and is not stored in this repository. See the
[data-quality report](docs/data-quality-report.md) for what the cleaning keeps, flags and
quarantines.

Open the repo in Claude Code and run `/bmad-help` to see where the project is and what comes next.
