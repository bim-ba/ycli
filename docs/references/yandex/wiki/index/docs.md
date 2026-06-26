---
name: wiki-docs-index
description: Comprehensive Yandex Wiki API reference — all endpoints, feature deep-dives, httpie workflows, and known gaps
type: index
---

# Wiki API — Comprehensive Reference

**Base URL:** `https://api.wiki.yandex.net`
**Auth header:** `Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN`
**Org header:** `X-Org-Id: $YANDEX_ID_ORGANIZATION_ID`

Note: Wiki uses `X-Org-Id` (capital I, lowercase d) — different from Tracker's `X-Org-ID`.

---

## Directory Map

Full API documentation lives in `../` (the section directories beside this index). Use this map to know which directory to read for each operation.

| Directory | Coverage | When to read |
|-----------|----------|-------------|
| `01-overview/` | Wiki concepts, page structure, content types | When unfamiliar with Wiki data model or terminology |
| `02-quick-start/` | Getting started with the Wiki API | When doing Wiki API work for the first time |
| `03-page-management/` | Page CRUD, copy, move, restore operations | **When creating, updating, or deleting pages** |
| `04-navigation/` | Page tree, children, descendants, search | When navigating the page hierarchy |
| `05-edit-page/` | YFM syntax reference, Include element, formatting | **When writing YFM content; for Include syntax** |
| `06-integrations/` | External integrations, DataLens embeds, iframes | When embedding DataLens dashboards or external content |
| `07-api/` | API overview, auth, error codes, base URLs | Read first if unfamiliar with Wiki API; check for auth issues |

## Most Commonly Used

For 80% of wiki agent tasks, you only need:

- `03-page-management/` — create/update pages
- `05-edit-page/` — YFM syntax (especially Include syntax)
- `07-api/` — auth troubleshooting

---

## All API Endpoints

### Pages — Core CRUD

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/pages?slug={slug}` | Get page metadata by slug |
| `GET` | `/v1/pages?slug={slug}&fields=content` | Get page with content (content not returned by default) |
| `GET` | `/v1/pages/{id}` | Get page by ID |
| `GET` | `/v1/pages/{id}?fields=content` | Get page by ID with content |
| `POST` | `/v1/pages` | Create a new page |
| `PATCH` | `/v1/pages/{id}` | Update page (title, content, etc.) |
| `DELETE` | `/v1/pages/{id}` | Delete a page (moves to trash) |

**Fields parameter** — request specific fields to reduce response size:

- `content` — YFM source text (not returned by default)
- `title`, `slug`, `id`, `createdAt`, `updatedAt`, `authorId`, `parentId`
- Comma-separate multiple: `?fields=content,title,slug`

**Create request body:**

```json
{
  "title": "Page Title",
  "slug": "data/guides/my-page",
  "content": "# Heading\n\nBody text here.",
  "parentId": "optional-parent-page-id"
}
```

**PATCH request body** (all fields optional — only send what changes):

```json
{
  "title": "Updated Title",
  "content": "# New content"
}
```

### Pages — Content Operations

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/pages/{id}/content/append` | Append content to the end of the page |

**Append body:**

```json
{"content": "\n## New Section\n\nContent added by agent."}
```

### Pages — Navigation / Tree

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/pages/children-by-slug?slug={slug}` | Get direct child pages of a slug |
| `GET` | `/v1/pages/descendants?slug={slug}` | Get all descendants (full subtree) of a slug |
| `GET` | `/v1/pages/descendants?slug={slug}&depth={n}` | Descendants up to n levels deep |
| `GET` | `/v1/pages/search?query={text}` | Full-text search across all pages |
| `GET` | `/v1/pages/search?query={text}&slug={prefix}` | Search within a slug prefix |

Both `children-by-slug` and `descendants` return `{"results": [...]}` arrays.

### Pages — Lifecycle (Copy / Move / Restore)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/pages/{id}/copy` | Copy a page to a new slug |
| `POST` | `/v1/pages/{id}/move` | Move a page to a new parent |
| `POST` | `/v1/pages/{id}/restore` | Restore a deleted page from trash |
| `GET` | `/v1/pages/{id}/history` | Get revision history of a page |
| `GET` | `/v1/pages/{id}/history/{revisionId}` | Get a specific historical revision |

**Copy body:**

```json
{"targetSlug": "data/guides/my-page-copy"}
```

**Move body:**

```json
{"parentId": "target-parent-page-id"}
```

### Pages — Async Clone Operation

For cloning large page trees, the API uses an async job model:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/pages/{id}/clone` | Start async clone of a page subtree |
| `GET` | `/v1/operations/{operationId}` | Poll clone operation status |

**Clone body:**

```json
{
  "targetSlug": "data/new-section",
  "deep": true
}
```

**Poll until done:**

```bash
http --print=b GET "https://api.wiki.yandex.net/v1/operations/{operationId}" \
  "Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN" \
  "X-Org-Id: $YANDEX_ID_ORGANIZATION_ID" | \
  uv run python -c "import sys,json; d=json.load(sys.stdin); print(d.get('status'), d.get('result',''))"
```

Operation statuses: `PENDING`, `IN_PROGRESS`, `DONE`, `FAILED`.

### Comments

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/pages/{id}/comments` | List all comments on a page |
| `POST` | `/v1/pages/{id}/comments` | Add a comment to a page |
| `PATCH` | `/v1/pages/{id}/comments/{commentId}` | Update a comment |
| `DELETE` | `/v1/pages/{id}/comments/{commentId}` | Delete a comment |

**Comment body:**

```json
{"text": "Comment text here"}
```

### Attachments

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/pages/{id}/attachments` | List attachments on a page |
| `GET` | `/v1/pages/{id}/attachments/{attachmentId}` | Get attachment metadata |
| `DELETE` | `/v1/pages/{id}/attachments/{attachmentId}` | Delete an attachment |

### Upload Sessions (File Attachments)

File upload uses a two-step session model:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/pages/{id}/attachments/upload-session` | Start an upload session, get upload URL |
| `PUT` | `{uploadUrl}` | Upload file bytes to the returned URL |
| `POST` | `/v1/pages/{id}/attachments/upload-session/{sessionId}/commit` | Finalize the upload |

**Start session body:**

```json
{"filename": "diagram.png", "mimeType": "image/png"}
```

Response contains `uploadUrl` and `sessionId`. PUT the binary content directly to `uploadUrl`, then commit.

### Grids (Dynamic Tables)

Grids are interactive tables embedded in wiki pages via `{% wgrid id="..." %}`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/grids/{gridId}` | Get grid metadata and schema |
| `POST` | `/v1/grids` | Create a new grid |
| `PATCH` | `/v1/grids/{gridId}` | Update grid metadata |
| `DELETE` | `/v1/grids/{gridId}` | Delete a grid |

**Rows:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/grids/{gridId}/rows` | List all rows |
| `POST` | `/v1/grids/{gridId}/rows` | Add a new row |
| `PATCH` | `/v1/grids/{gridId}/rows/{rowId}` | Update a row |
| `DELETE` | `/v1/grids/{gridId}/rows/{rowId}` | Delete a row |

**Columns:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/grids/{gridId}/columns` | List all columns |
| `POST` | `/v1/grids/{gridId}/columns` | Add a column |
| `PATCH` | `/v1/grids/{gridId}/columns/{columnId}` | Update a column definition |
| `DELETE` | `/v1/grids/{gridId}/columns/{columnId}` | Delete a column |

**Cells:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/grids/{gridId}/rows/{rowId}/cells` | Get all cells in a row |
| `PATCH` | `/v1/grids/{gridId}/rows/{rowId}/cells/{columnId}` | Update a single cell value |

**Grid create body:**

```json
{
  "title": "Sprint Tasks",
  "columns": [
    {"id": "task", "title": "Task", "type": "string"},
    {"id": "status", "title": "Status", "type": "string"},
    {"id": "owner", "title": "Owner", "type": "string"}
  ]
}
```

Column types: `string`, `number`, `boolean`, `date`, `link`, `user`.

**Embed grid in a page:**

```yfm
{% wgrid id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" %}
```

With display options:

```yfm
{% wgrid id="uuid" readonly="1" num="1" sort="0" columns="task,status" filter="[Status]='Active'" %}
```

---

## Feature Deep-Dives

For per-resource detail (request shapes, examples, edge cases), see:

- [endpoints/pages-crud.md](endpoints/pages-crud.md) — Create / read / update / delete pages
- [endpoints/descendants.md](endpoints/descendants.md) — Tree navigation
- [endpoints/append-content.md](endpoints/append-content.md) — Append-only writes
- [endpoints/grids.md](endpoints/grids.md) — Dynamic tables full workflow
- [endpoints/comments.md](endpoints/comments.md) — Page comments
- [endpoints/attachments.md](endpoints/attachments.md) — Attachments + upload sessions
- [endpoints/async-clone.md](endpoints/async-clone.md) — Async clone operations
- [endpoints/yfm-authoring.md](endpoints/yfm-authoring.md) — YFM markup reference
- [endpoints/include.md](endpoints/include.md) — Include / transclude pattern
- [endpoints/recovery.md](endpoints/recovery.md) — Restore deleted pages

## Common httpie Workflow Patterns

See [endpoints/workflows.md](endpoints/workflows.md) for end-to-end patterns
(slug→id lookup, edit-and-write-back, build slug maps, template-driven creates, etc.).

---

## Gaps and Limitations

| Area | Limitation |
|------|-----------|
| **Content default** | `content` field is never returned unless explicitly requested with `?fields=content` |
| **WYSIWYG pages** | Pages created in the visual editor contain binary control characters in the content field — `jq` will fail; always use `uv run python` |
| **Slug immutability** | Slugs cannot be renamed after creation — all existing links break if a slug changes |
| **`get-by-slug` endpoint** | `/v1/pages/get-by-slug` returns 404 — use `GET /v1/pages?slug={slug}` instead |
| **Search scope** | Full-text search may not index pages immediately after creation; allow 30–60 seconds |
| **Clone async** | `POST /v1/pages/{id}/clone` is async — poll `/v1/operations/{id}` for completion |
| **No bulk PATCH** | There is no endpoint to update multiple pages in one request — loop page-by-page |
| **Include rendering** | `{{include}}` is rendered server-side; the API returns the raw `{{include ...}}` tag, not the included content |
| **Grid filter syntax** | Grid `filter` parameter uses a custom expression language: `[ColumnTitle]='Value'` — column names are case-sensitive display titles |
| **Attachment binary upload** | The PUT to `uploadUrl` must send raw binary; httpie's `@file` sends as multipart — use `--ignore-stdin` and pipe binary directly or use a raw PUT |
| **Org ID format** | Header name is `X-Org-Id` (capital I, lowercase d) — mistyping as `X-Org-ID` causes auth errors |
