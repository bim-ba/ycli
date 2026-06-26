# Comments — Tracker API

← Back to [docs.md](../docs.md)

## Comments, Reactions, Checklists (`18-api/tasks/comments/`, `checklists/`)

**Comments:**

- `POST /v3/issues/{key}/comments/` — add comment (`text` field, supports wiki markup)
- `GET /v3/issues/{key}/comments/` — list all comments
- `PATCH /v3/issues/{key}/comments/{id}` — edit comment
- `DELETE /v3/issues/{key}/comments/{id}` — delete comment

**Reactions (emoji):**

- `POST /v3/issues/{key}/comments/{id}/reactions` — add reaction (`reaction` field, e.g., `"like"`)

**Checklists:**

- `POST /v3/issues/{key}/checklistItems` — add item (`text`, optional: `assignee`, `deadline`, `checked`)
- `GET /v3/issues/{key}/checklistItems` — list all checklist items
- `PATCH /v3/issues/{key}/checklistItems/{id}` — update item (toggle `checked`, change assignee)
- `DELETE /v3/issues/{key}/checklistItems/{id}` — remove item

Checklist items support per-item `assignee` (different from issue assignee) and `deadline` (ISO date).
