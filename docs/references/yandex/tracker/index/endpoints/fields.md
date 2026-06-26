# Fields — Tracker API

← Back to [docs.md](../docs.md)

## Fields: Global and Local (`18-api/fields/`)

**Global fields** (available in all queues):

- `GET /v3/fields/` — list all global fields
- `GET /v3/fields/{id}/values` — list allowed values for enum-type fields (e.g., priorities, resolutions)

**Local queue fields** (defined per queue):

- `GET /v3/queues/{id}/localFields/` — list local fields for a specific queue
- Local fields have IDs prefixed with the queue key

**Field types:** string, integer, float, date, datetime, user, enum (single/multi), checkbox, url

Use `GET /v3/fields/` to discover field IDs before referencing them in issue create/update payloads.
