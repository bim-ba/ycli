# Agile — Tracker API

← Back to [docs.md](../docs.md)

## Agile: Boards and Sprints (`07-agile/`, `18-api/boards/`)

**Board CRUD:**

- `POST /v3/boards/` — create (type: `scrum` or `kanban`), set columns and mapping to statuses
- `GET /v3/boards/` — list all boards; `PATCH /v3/boards/{id}` — update board settings
- `GET /v3/boards/{id}/columns` — list columns; `PATCH /v3/boards/{id}/columns/{id}` — update column

**Sprint lifecycle:**

```text
create → start → (work) → archive
```

- `POST /v3/boards/{id}/sprints` — create sprint (`name`, `startDate`, `endDate`)
- `POST /v3/boards/{id}/sprints/{id}/start` — start sprint (moves to active)
- `POST /v3/boards/{id}/sprints/{id}/archive` — archive sprint (close out)
- `GET /v3/boards/{id}/sprints` — list sprints with status filter (`open`, `active`, `archived`)

Add issues to sprint via PATCH on the issue: `sprint: [{"id": <sprintId>}]`
