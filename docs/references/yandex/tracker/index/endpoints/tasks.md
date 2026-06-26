# Tasks — Tracker API

← Back to [docs.md](../docs.md)

## Issue/Task Operations (`18-api/tasks/`)

All methods and paths:

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/v3/issues/` | Create issue |
| `GET` | `/v3/issues/{key}` | Get issue by key or ID |
| `PATCH` | `/v3/issues/{key}` | Update issue fields |
| `DELETE` | `/v3/issues/{key}` | Delete issue |
| `POST` | `/v3/issues/_search` | Search with filter object |
| `GET` | `/v3/issues/{key}/transitions` | List available transitions |
| `POST` | `/v3/issues/{key}/transitions/{id}/_execute` | Execute transition |
| `POST` | `/v3/issues/{key}/move` | Move to a different queue |
| `GET` | `/v3/issues/{key}/history` | Get field change history |

**Key fields for create (`POST /v3/issues/`):**

- Required: `queue` (key or `{id}`), `summary`
- Common: `type` (`{key: "task"|"bug"|"story"|"epic"|"improvement"|"incident"|"refactoring"}`), `priority` (`{key: "critical"|"high"|"normal"|"low"}`), `description`, `assignee` (login), `parent` (key), `sprint` (`[{id}]`), `end` (ISO date), `storyPoints`

**Key fields for update (`PATCH /v3/issues/{key}`):**

- Any subset of creation fields; use `{key}` objects for enum fields (type, priority, resolution)
- Resolution values: `successful`, `fixed`, `wontFix`, `cantReproduce`

**Search syntax (`POST /v3/issues/_search`):**

```json
{
  "filter": {"queue": "DATAENGINEERING", "status": ["inProgress"], "assignee": "login"},
  "query": "Queue: DATAENGINEERING AND Status: InProgress",
  "order": ["+priority", "-updatedAt"],
  "perPage": 50,
  "page": 1,
  "scrollType": "sum"
}
```

Use either `filter` (structured) or `query` (Tracker Query Language string), not both. Three pagination modes: `page`/`perPage` (simple), `scrollType: sum` (relative scroll), `scrollType: relativeScroll` with `lastTicket` (keyset).
