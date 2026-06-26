# Attachments — Tracker API

← Back to [docs.md](../docs.md)

## File Attachments (`18-api/tasks/files/`)

**Standard upload:**

- `POST /v3/issues/{key}/attachments/` — upload file (multipart/form-data)
- `GET /v3/issues/{key}/attachments/` — list attachments
- `DELETE /v3/issues/{key}/attachments/{id}` — delete attachment

**Temporary upload workflow** (attach before issue exists):

1. `POST /v3/issues/{key}/attachments/upload` — upload to temp storage, get `tempAttachmentId`
2. Reference `tempAttachmentId` in the issue create/update payload

**Thumbnails:** Images generate a thumbnail URL accessible via the attachment metadata.
