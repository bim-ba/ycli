# Queues — Tracker API

← Back to [docs.md](../docs.md)

## Queue Management (`05-queue/`, `18-api/queues/`)

| Endpoint | Purpose |
|----------|---------|
| `POST /v3/queues/` | Create queue |
| `GET /v3/queues/` | List all queues |
| `GET /v3/queues/{id}` | Get queue details (id or key) |
| `PATCH /v3/queues/{id}` | Update queue settings |
| `DELETE /v3/queues/{id}` | Delete queue |
| `GET /v3/queues/{id}/components/` | List components |
| `POST /v3/queues/{id}/components/` | Create component |
| `GET /v3/queues/{id}/versions` | List versions |
| `GET /v3/queues/{id}/tags` | List tags |
| `GET /v3/queues/{id}/requiredFields` | List required fields per transition |

Queue IDs for our queues: `DATAENGINEERING` = 6, `BI` board = 10, `DATAPRODUCT` board = 32, `DATAENGINEERING` board = 34, `ADHOC` board = 37.

Note: Workflow structure (statuses, transitions, required fields) is configured in the Tracker UI only — the API cannot create or modify workflow structure.
