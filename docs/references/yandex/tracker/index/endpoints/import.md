# Import — Tracker API

← Back to [docs.md](../docs.md)

## Import API (`18-api/import/`)

Bulk import endpoints for migrating data from external systems:

| Endpoint | Purpose |
|----------|---------|
| `POST /v3/issues/_import` | Import issues with full metadata (preserves created/updated dates) |
| `POST /v3/issues/{id}/comments/_import` | Import comments with original author and date |
| `POST /v3/issues/{id}/attachments/_import` | Import attachments |
| `POST /v3/issues/{id}/worklog/_import` | Import worklog entries |
| `POST /v3/issues/{id}/links/_import` | Import issue links |

**Caveats:**

- Import API preserves original `createdAt`/`updatedAt` timestamps (unlike regular create)
- Requires special import permissions — not available to all OAuth tokens
- Idempotency: re-importing the same external ID updates rather than duplicates
- For large imports, combine with bulk operations where possible
