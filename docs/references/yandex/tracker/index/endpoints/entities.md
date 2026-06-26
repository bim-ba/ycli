# Entities — Tracker API

← Back to [docs.md](../docs.md)

## Entity API: Projects, Portfolios, Goals (`08-entities/`, `18-api/entities/`)

`POST /v3/entities/{type}/` where `type` is one of: `project`, `portfolio`, `goal`

**Create a project:**

```bash
http POST 'https://api.tracker.yandex.net/v3/entities/project/' \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" "X-Org-ID: $YANDEX_ID_ORGANIZATION_ID" \
  fields:='{"summary": "My Project", "teamUsers": [{"login": "user1"}]}'
```

**Entity sub-resources** (all entities share these endpoints):

- Comments: `POST /GET /v3/entities/{id}/comments`
- Files/Attachments: `POST /GET /v3/entities/{id}/files`
- Links: `POST /GET /DELETE /v3/entities/{id}/links`
- Checklists: `POST /GET /PATCH /DELETE /v3/entities/{id}/checklists`

**Bulk entity edit:** `POST /v3/entities/_bulk_edit` — update fields on multiple entities at once.

**Key result metrics** and goal progress are managed as sub-fields on the entity object.
