# Search — Tracker API

← Back to [docs.md](../docs.md)

## Search with Filters (`09-tasks/`, `18-api/tasks/search`)

`POST /v3/issues/_search` supports two filter modes:

**Structured filter object** (recommended for programmatic use):

```json
{"filter": {"queue": "DATAENGINEERING", "status": ["inProgress", "testing"], "type": "task"}}
```

**Tracker Query Language** (for complex conditions):

```text
Queue: DATAENGINEERING AND Status: InProgress AND Assignee: login AND "Story Points": > 3
```

**Pagination modes:**

- Simple: `"page": 1, "perPage": 100` (max 10,000 total results)
- Relative scroll: `"scrollType": "sum", "perPage": 100` — returns `X-Total-Count` header
- Keyset: `"scrollType": "relativeScroll", "lastTicket": "DATAENGINEERING-100"` — for large result sets

**Saved filters:** `POST /v3/filters/` — save a search for reuse; `GET /v3/filters/` — list saved filters.
