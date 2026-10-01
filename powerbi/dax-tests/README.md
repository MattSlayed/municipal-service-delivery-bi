# DAX tests

Each `.dax` file compares Power BI measures with the values the pipeline computed independently
(`data/processed/reference_values.json`). The pipeline is plain pandas, so a match means two
separate implementations of the same rule agree.

| Test | Measures | Checks |
|---|---|---:|
| `01-open-active-stuck.dax` | Open Now, Active, Stuck | 4 dates |
| `02-weekly-flow.dax` | Requests In, Completions, Net Change | 52 weeks of 2020 |
| `03-avg-weekly-completions.dax` | Avg Weekly Completions | 51 section-dates |
| `04-weeks-to-clear.dax` | Weeks to Clear, including where it must be blank | 51 section-dates |
| `05-contractor-flag.dax` | Contractor Flag, Flagged Sections | 51 section-dates and 4 counts |
| `06-suburb-rank.dax` | Suburb Rank, suburb Weeks to Clear, Unknown Suburb Active | Top 10 suburbs in every flagged section |

Every test returns one row: the number of checks, how many passed, **PASS** or **FAIL**, and the
first failure. The reference dates are 31 March, 30 June, 30 September and 31 December 2020; the
contractor flag is tested at the default threshold of 3 weeks.

## Running a test

1. Open `MunicipalServiceDelivery.pbip` in Power BI Desktop and refresh, so the model holds the
   same data the reference values were computed from.
2. Open **DAX query view**, paste the contents of a file and select **Run**.

The tests can also be run through the Power BI Authoring MCP server
(`dax_query_operations` → `Execute`; see [`../mcp-setup.md`](../mcp-setup.md)).

## Regenerating

The expected values are written into the files. After a pipeline change, regenerate them:

```
uv run python -m pipeline.run
uv run python scripts/build_dax_tests.py
```

Do not edit the `.dax` files by hand.
