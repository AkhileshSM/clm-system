# Jira MCP Integration

The backend reads sprint workload data through the `SprintsDataProvider` interface.
This keeps scoring and API endpoints independent from whether data comes from mock
JSON or a real Jira MCP server.

## Provider Selection

Use mock data:

```bash
DATA_PROVIDER=mock
```

Use a Jira MCP server:

```bash
DATA_PROVIDER=jira_mcp
JIRA_MCP_URL=http://localhost:3001/mcp
JIRA_MCP_SPRINT_TOOL=jira_get_current_sprint
JIRA_MCP_ENGINEER_TOOL=jira_get_engineer_workload
```

`JIRA_MCP_SPRINT_TOOL` and `JIRA_MCP_ENGINEER_TOOL` are optional if the MCP server
uses the default tool names above.

## MCP Tool Contract

The sprint tool should return either:

- An array of engineer workload records.
- An object with one of these array keys: `engineers`, `assignees`, `workloads`,
  or `issues`.

The engineer tool is called with:

```json
{
  "engineer_id": "engineer-or-jira-account-id"
}
```

The backend accepts records already shaped like the `Engineer` schema. If the MCP
server returns Jira-flavored records, the provider normalizes fields such as
`assignee`, `issues`, `priority`, `status`, and `story_points` into the CLM model.

## Data Gaps

Jira usually provides tickets, statuses, priorities, assignees, sprint membership,
and story points. The CLM model also uses human-load signals such as repo ownership,
production support responsibility, meeting load, dependencies, and context switching.
Those fields should come from Jira custom fields, another internal provider, or
computed heuristics before scoring.

## Simulation Endpoint

`POST /api/simulate/incident` mutates `mock-data/sprint_data.json`. It is disabled
when `DATA_PROVIDER=jira_mcp` because real Jira data should not be changed by the
demo simulation endpoint.
