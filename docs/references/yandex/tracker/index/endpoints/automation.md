# Automation — Tracker API

← Back to [docs.md](../docs.md)

## Automation: Triggers, Macros, Autoactions (`13-automation/`, `18-api/queues/triggers/`, `autoactions/`, `macros/`)

**Triggers** — fire on issue events (field change, status change, comment added):

- `POST /v3/queues/{id}/triggers/` — create trigger with `conditions` and `actions`
- Actions can include: change field value, set status, add comment, send webhook, create issue
- Variable substitution: `{{issue.summary}}`, `{{issue.assignee.login}}`, `{{issue.status.key}}`
- Execution logs: `GET /v3/queues/{id}/triggers/{id}/logs` — use to debug trigger failures

**Macros** — manual one-click actions on an issue (no conditions):

- `POST /v3/queues/{id}/macros/` — create; `DELETE /v3/queues/{id}/macros/{id}` — remove
- Can add comments, change fields, execute transitions

**Autoactions** — scheduled or threshold-based automation (e.g., auto-close stale issues):

- `POST /v3/queues/{id}/autoactions/` — create with `filter`, `conditions`, `actions`, `schedule`
- Execution logs: `GET /v3/queues/{id}/autoactions/{id}/logs`

**Triggers vs Macros vs Autoactions:**

- Trigger: event-driven, automatic, complex conditions
- Macro: manual, user-initiated, no conditions
- Autoaction: scheduled/threshold, automatic, simpler than triggers
