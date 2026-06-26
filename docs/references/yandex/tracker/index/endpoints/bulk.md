# Bulk Operations — Tracker API

← Back to [docs.md](../docs.md)

## Bulk Operations (`18-api/bulk/`) — High Impact

`POST /v3/bulkchange/_update` — update fields on up to 10,000 tasks in a single async request.

```bash
echo '{
  "issues": ["DATAENGINEERING-1", "DATAENGINEERING-2"],
  "values": {"priority": {"key": "high"}, "assignee": "login"}
}' | http --print=b POST 'https://api.tracker.yandex.net/v3/bulkchange/_update' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID"
```

`POST /v3/bulkchange/_move` — move issues to a different queue in bulk.

**Async status check** — the response contains an operation ID; poll until complete:

```bash
http --print=b GET 'https://api.tracker.yandex.net/v3/bulkchange/_status/{operationId}' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID"
```

Response `.status` values: `CREATED`, `IN_PROGRESS`, `COMPLETED`, `FAILED`.

**When to use bulk vs individual PATCH:** Use bulk when updating 3+ issues with the same field change. Individual PATCH is more appropriate for unique per-issue values or when you need per-issue error handling.
