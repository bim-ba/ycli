# Worklog — Tracker API

← Back to [docs.md](../docs.md)

## Worklog / Time Tracking (`18-api/worklog/`)

**Per-issue worklog:**

- `POST /v3/issues/{key}/worklog` — log time (`duration` in ISO 8601 duration format, e.g., `"PT2H30M"`, plus optional `comment` and `start` datetime)
- `GET /v3/issues/{key}/worklog` — list worklog entries for an issue
- `PATCH /v3/issues/{key}/worklog/{id}` — update worklog entry
- `DELETE /v3/issues/{key}/worklog/{id}` — delete entry

**Cross-issue worklog search:**

- `POST /v3/worklog/_search` — search worklog entries across issues by user, date range, or queue
