# Power BI Authoring MCP: set-up with Claude Code (Windows)

The [Power BI Authoring MCP server](https://github.com/microsoft/powerbi-modeling-mcp) lets an AI
agent read and change a Power BI semantic model, and run DAX queries against it. This project uses
it to build routine parts of the model and to test measures against the pipeline's reference
values. It cannot create report pages or visuals.

Microsoft's recommended route is VS Code with GitHub Copilot. This project uses the documented
manual route for other MCP clients.

## Requirements

- Power BI Desktop (Microsoft Store version)
- Node.js (for `npx`)
- Claude Code

## 1. Register the server

```powershell
claude mcp add --scope user powerbi-authoring-local -- npx -y @microsoft/powerbi-modeling-mcp@1.0.0 --start
claude mcp get powerbi-authoring-local   # Status should read "Connected"
```

The version is pinned. The server changed its name, authentication and defaults several times
during its preview, and `@latest` could change behaviour between two working sessions.

## 2. Accept the licence

The server blocks every tool until its [licence (EULA)](https://github.com/microsoft/powerbi-modeling-mcp/blob/main/EULA.txt)
is accepted. Read it, then in a Claude Code session tell the agent explicitly that you accept it.
The agent calls the server's `accept_eula` tool, and the acceptance is saved on this machine.

Do not add `--accepteula` or `PBI_MODELING_MCP_ACCEPT_EULA=true` to any configuration committed
to this repository: that would accept the licence on behalf of anyone who clones it.

## 3. Connect to the model

1. Open `MunicipalServiceDelivery.pbip` (repository root) in Power BI Desktop and leave it open.
2. Start Claude Code (MCP servers load when a session starts) and ask:
   `Connect to 'MunicipalServiceDelivery' in Power BI Desktop`

Before any session that changes the model, commit to git: git is the undo.

## What changes Desktop shows immediately, and what it does not

Measures, descriptions, formats and other property changes made through the MCP appear in Desktop
straight away. **New tables, partitions and Power Query parameters do not**: they exist in the
engine, but Desktop's screen never shows them. For those, export the model to the project's TMDL
folder, close Desktop **without saving**, reopen the `.pbip` and refresh:

```
database_operations ExportToTmdlFolder → <Project>.SemanticModel\definition
```

Then restore `definition\database.tmdl` to Desktop's own two-line form (`database` and
`compatibilityLevel`); the export writes the live session's internal ID into it.

## Data sent to the AI provider

The server sends model metadata and query results to the MCP client, which may pass them to the
LLM provider. That is acceptable here because the data is published open data. It would not be
for a model holding personal information.
