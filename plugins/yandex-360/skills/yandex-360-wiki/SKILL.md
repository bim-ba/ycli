---
name: yandex-360-wiki
description: Use when reading or writing Yandex Wiki pages through ycli — page content and metadata, full-text search, the page tree, moving or renaming pages, revision history, backlinks, grids, comments, attachments, page access, YFM authoring — via the CLI, MCP, or Python SDK.
metadata:
  category: workflow
---

# Yandex Wiki

Drive Yandex Wiki (Yandex 360) through `ycli`: search pages by text; read page content, metadata, tree, comments and attachments; create, update, clone and delete pages with YFM; manage grids (dynamic tables), attachments and page access. Reads **and writes** ship on all three surfaces — the CLI, the `wiki_*` MCP tools, and the Python SDK — plus the API's real-world quirks.

## When to use

- An agent needs context from the Wiki: read a page's content or metadata, walk a subtree, list comments or attachments.
- An agent needs to create or update a page with YFM content (notes, tabs, cuts, layouts, tables, diagrams, includes), clone a page, comment, attach files, or manage a grid.

## When NOT to use

- Tracker issue management — use the `yandex-360-tracker` skill.
- Yandex Forms — use the `yandex-360-forms` skill.

You can read any section you have access to and write where you have permission. Replace the placeholder slugs in the examples below (`your-space/page`, `team/architecture/overview`, …) with real slugs from your organization.

---

## 1. Auth and tools

**Authentication** (via environment):

```text
Authorization: OAuth $YANDEX_ID_OAUTH_TOKEN
X-Org-Id: $YANDEX_ID_ORGANIZATION_ID
```

> The org id goes in one canonical header, `X-Org-Id`, for every Yandex 360 service — the same header Tracker and Forms use. HTTP header names are case-insensitive (RFC 9110), so casing never matters; the CLI/SDK set it for you.

**Three ways in:**

| Surface | What it covers |
|---------|----------------|
| **CLI** — `uv run ycli wiki <group> <cmd>` | Everything: `pages get\|create\|update\|append\|clone\|move\|delete\|descendants\|revisions\|backlinks`, `search`, `access`, `comments`, `grids`, `attachments` (incl. binary download and preview), `uploadsessions`, `recovery`, `operations` |
| **MCP tools** (reads and writes) | Named `wiki_<resource>_<action>` — reads like `wiki_pages_get`, `wiki_pages_meta`, `wiki_pages_descendants`, `wiki_search_query`, `wiki_comments_list`, `wiki_attachments_list`, `wiki_pages_revisions_list`, `wiki_pages_backlinks_list`, plus write tools for pages create/update/append/clone/move/delete, page access, comments, grids CRUD, attachment upload (base64) and delete. Writes carry honest annotations (`readOnlyHint=False`, explicit `destructiveHint`); `ycli mcp start --read-only` hides them. Binary **downloads and previews** stay CLI/SDK-only. |
| **Python SDK** | `from ycli.yandex.wiki.client import WikiClient` → `WikiClient(oauth_token=…, organization_id=…)` exposes `.pages`, `.search`, `.access`, `.comments`, `.grids`, `.attachments`, `.uploadsessions`, `.resources`, `.recovery`, `.operations` — full read/write parity with the CLI. |

**Prefer the CLI / MCP tools over raw `http` calls** — they encode the API quirks (header name, `slug=` query form, POST-not-PATCH, `fields=` rules) correctly.

Full Wiki API reference lives online at <https://yandex.ru/dev/wiki/> (developer portal) and <https://yandex.ru/support/wiki/> (product docs). For YFM authoring syntax, see the bundled `references/yfm-quick-ref.md`.

---

## 2. Reading

Every read is available both as a CLI command and as an MCP tool (annotated `readOnlyHint=True`).

| Operation | CLI command | MCP tool |
|-----------|-------------|----------|
| Full page content | `uv run ycli wiki pages get <slug>` | `wiki_pages_get` |
| Metadata only (id, title, owner, timestamps) | `uv run ycli wiki pages get <slug> --fields attributes` | `wiki_pages_meta` |
| Content **and** metadata in one call | `uv run ycli wiki pages get <slug> --fields content,attributes` | — |
| Descendant slugs (auto-paginated) | `uv run ycli wiki pages descendants <slug> [--limit N \| --all]` | `wiki_pages_descendants` |
| Full-text search (one page of hits) | `uv run ycli wiki search query <text> [--type page\|file] [--cluster <slug>] [--limit N] [--cursor N]` | `wiki_search_query` |
| A page's saved revisions, newest first ¹ | `uv run ycli wiki pages revisions-list <page_id> [--ids 1,2] [--limit N \| --all]` | `wiki_pages_revisions_list` |
| Pages that link to a page ¹ | `uv run ycli wiki pages backlinks-list <page_id> [--for-cluster] [--limit N \| --all]` | `wiki_pages_backlinks_list` |
| One attachment's metadata ¹ | `uv run ycli wiki attachments get <page_id> <file_id>` | `wiki_attachments_get` |
| Is a grid column slug free? ¹ | `uv run ycli wiki grids columns suggest <grid_id> (--title T \| --slug S)` | `wiki_grids_columns_suggest` |
| Who may open a page, and its personal accesses | `uv run ycli wiki pages get-by-id <page_id> --fields access_policy,access_lists,owner` | `wiki_pages_get_by_id` |
| Comments on a page | **2-step** (see below) | `wiki_comments_list` |
| Attachments on a page | **2-step** (see below) | `wiki_attachments_list` |

```bash
# Page content
uv run ycli wiki pages get your-space/page

# Metadata only — note --fields REPLACES the default (content); body is NOT returned
uv run ycli wiki pages get your-space/page --fields attributes

# Both at once
uv run ycli wiki pages get your-space/page --fields content,attributes
```

### Tree navigation

`pages descendants` follows the cursor itself and returns the `{id, slug}` refs of the whole subtree, up to the configured item cap (`YCLI__HTTP__MAX_ITEMS`). Pass `--limit N` for fewer, or `--all` to ignore the cap.

```bash
uv run ycli wiki pages descendants team
uv run ycli wiki pages descendants team --all   # a subtree larger than the cap
```

Use this to build a slug→title map of a subtree, then `pages get <slug> --fields attributes` per slug for titles.

¹ **Undocumented by Yandex** (see [Undocumented operations](#undocumented-operations)).

### Comments and attachments — the 2-step get-id-then-list pattern

The comments/attachments endpoints key off the numeric page **id**, not the slug. So:

```bash
uv run ycli wiki pages get your-space/page    # → read the "id" field from the output
uv run ycli wiki comments list <page_id>
uv run ycli wiki attachments list <page_id>
```

### Search

`wiki search query` runs the Wiki's full-text search and prints one page of hits (`slug`, `title`, `content` snippet, `type`, `modified_at`). Read a hit with `pages get <slug>`.

```bash
uv run ycli wiki search query "quarterly roadmap" --type page --cluster team --limit 20
uv run ycli wiki search query roadmap --cursor 2          # the next page: pass next_cursor back as --cursor
```

- **Paging is by hand.** `next_cursor` is the next page's number (`"2"`). The API also sets it after an empty page and repeats hits for a page past the last one, so stop at the first page with no hits instead of waiting for `null`. At most 500 pages and 50 hits per page.
- **A date window needs both ends** (`--created-from` with `--created-to`, `--modified-from` with `--modified-to`): the API answers an open-ended window with 400.
- `--highlight` wraps the matches in `<em>`; `--order-by relevancy|creation_date|modified_date`; `--author-uid` / `--author-cloud-uid` filter by author.
- A page you just created can take a few seconds to show up in the index.

---

## 3. Writing

Writes ship on **SDK + CLI + MCP** (write tools carry `readOnlyHint=False` and explicit destructive hints). The core flow is `pages create` / `pages update` (MCP: `wiki_pages_create` / `wiki_pages_update`); §3.1 covers the rest of the write surface. The simplest flow: author the page body in a local YFM file, then publish it.

### Before you write

- **Decide the slug first.** Treat slugs as **permanent**: `pages move` can rename a page, but the old address then answers 404, so every inbound link and magic-link reference breaks. Format: `parent/child`, kebab-case, no spaces, no underscores, no Cyrillic.
- **If creating a child page, verify the parent exists**: `uv run ycli wiki pages get parent/path --fields attributes`.
- **Strip YAML frontmatter from the body yourself.** If your local file has `---` frontmatter, the CLI does **not** strip it and does **not** lift `title:` out of it — pass only the body (starting at the `# H1`) to `--content`, and pass the title separately via `--title`.

### Create

```bash
uv run ycli wiki pages create \
  --slug team/architecture/overview \
  --title 'Architecture Overview' \
  --content "$(cat body.md)"
```

### Update

```bash
# 1. Get the numeric page id
uv run ycli wiki pages get team/architecture/overview   # → read the "id" field

# 2. Republish (the API rejects PATCH with 405; the CLI always uses POST)
uv run ycli wiki pages update <page_id> \
  --content "$(cat body.md)" \
  [--title 'New title']
```

### Verify

```bash
uv run ycli wiki pages get team/architecture/overview
```

Confirm the published body starts at the `# H1`, not at `---` (which would mean frontmatter leaked through).

### 3.1. The rest of the write surface (all live-verified 2026-07-12)

| Operation | CLI | MCP tool |
|-----------|-----|----------|
| Append to a page | `uv run ycli wiki pages append <page_id> --content … --location top\|bottom` | `wiki_pages_append` |
| Clone a page (async) | `uv run ycli wiki pages clone <page_id> --target <new/slug> [--title …]` → poll `operations clone-get <task>` | `wiki_pages_clone` + `wiki_operations_clone_get` |
| Move or rename a page (async) ¹ | `uv run ycli wiki pages move <old/slug> <new/slug> [--validate-only] [--next-to <slug> --position before\|after] [--copy-inherited-access]` (waits by default; `--no-wait` to skip) | `wiki_pages_move` + `wiki_operations_move_get` |
| Delete / restore a page | `uv run ycli wiki pages delete <page_id>` (emits a `recovery_token`) → `uv run ycli wiki recovery restore <token>` | `wiki_pages_delete` / `wiki_recovery_restore` |
| Comments | `uv run ycli wiki comments create <page_id> --body … [--parent-id N]` / `… delete <page_id> <comment_id>` | `wiki_comments_create` / `wiki_comments_delete` |
| Page access | `uv run ycli wiki access create <page_id> --role reader\|editor\|extra_editor\|author (--user-uid U \| --group-src dir --group-id G) [--inheritance …]` / `access update <page_id> <access_id> --role …` / `access delete <page_id> <access_id>` / `access clear <page_id>` | `wiki_access_create` / `wiki_access_update` / `wiki_access_delete` / `wiki_access_clear` |
| Grids (dynamic tables) | `uv run ycli wiki grids create\|update\|clone\|delete`, `grids columns add\|move\|remove\|update ¹`, `grids rows add\|move\|remove\|update ¹`, `grids cells update` | `wiki_grids_*` (full CRUD) |
| Attachments | `uv run ycli wiki attachments upload <page_id> <file>` (single call) or the `uploadsessions create → upload-part → finish → attachments attach` pipeline; `attachments delete` | `wiki_attachments_upload` (base64), `wiki_uploadsessions_*`, `wiki_attachments_attach`, `wiki_attachments_delete` |

Attachment/keyset-style **downloads** (`attachments download`, `download-by-url`, `preview ¹`) are CLI/SDK-only — MCP excludes raw binary payloads (uploads are the exception: the wiki MCP upload tools take base64 input).

**Grid writes are optimistic-locked:** every grid mutation takes `--revision` (read the current revision from `grids get` first; each write bumps it).

Live-verified gotchas for these writes:

- **`pages append` defaults to `--location bottom`.** The API requires exactly one placement selector (`Fields ('body', 'section', 'anchor') are mutually exclusive`); ycli now always sends one — pass `--location top` to prepend.
- **`grids columns add` requires an explicit per-column `"slug"`.** `[{"title":"Count","type":"number","slug":"count"}]` works; omitting `slug` 400s (`value_error.missing`) despite older docs claiming it is server-generated.
- **Grid `default-sort` has a different write shape than its read shape.** The API *writes* a mapping list `[{"<column_slug>": "asc"}]` (read shape is `[{"slug","title","direction"}]`); ycli's `--default-sort` sends the write shape and rejects the read shape loudly.
- **Page access: pass `--prevent-selflock` on update, delete and clear.** The API then refuses a change that would leave you without read access or the right to change accesses. The page owner's own entry can be neither changed nor revoked, `access clear` keeps it, and granting a user who already has a personal access is refused (use `access update`). Read the entries (and their ids) back with `pages get-by-id <page_id> --fields access_policy,access_lists`. Verified live 2026-10-02.
- **`comments thread-get` returns nothing.** The server's `/thread` endpoint answers an empty list for every real thread, so use `comments thread-list` (rebuilt from `comments list`).
- **`attachments list` rows carry the numeric file `id`** that `get`, `download`, `preview` and `delete` take (the upload/attach response has it too).

### Undocumented operations

Yandex's live OpenAPI (<https://api.wiki.yandex.net/v1/openapi.json>) has 9 operations its documentation does not cover. ycli wraps all of them; they are marked ¹ above, say so in their `--help`, and **may change without notice**. What a live check (2026-10-03) found:

- **`pages move` is the only way to rename or relocate a page** (a page update has no `slug`). It moves the page with its whole subtree (`page_count` in the status counts both) and the old address answers 404 afterwards. The API refuses a move that does not say whether to copy inherited access (400 `INHERITANCE_BEHAVIOR_IS_NOT_SPECIFIED`), so ycli always sends `--copy-inherited-access` or `--no-copy-inherited-access` (the default). `--validate-only` only validates the request: nothing moves and its task id answers 404 when polled, so `--wait` is skipped. The target's parent must exist (400 `NO_PARENT_PAGE`), and `--next-to` must name a page that already sits where the target will (400 `NEXT_TO_WRONG_CLUSTER`); the API accepts it without `--position`.
- **`pages revisions-list` lists newest first.** A revision `id` is what the API's `GET /pages` takes as `revision_id` (`pages get` has no flag for it yet); `--ids` keeps only those. A fresh page has one revision per save.
- **`pages backlinks-list` lags a few seconds** behind the page that holds the link. `--for-cluster` also reports links to the page's descendants; plain lists links to the page only.
- **`attachments preview` returns an image only for an attachment with `has_preview: true`.** For one without (a text file, say) the API answers `200 image/png` whose body is the *base64 text* of a 1-pixel PNG, not the PNG; `attachments get` shows `has_preview`. A fresh upload reports `has_preview: false` for a few seconds.
- **`grids columns suggest` takes exactly one of `--title` and `--slug`** (400 for neither or both) and changes nothing. The server writes slugs with hyphens (`Due date` → `due-date`), where `grids columns add` derives them with underscores.
- **`grids columns update` and `grids rows update` do not enforce `--revision`**: a stale or missing one is accepted, and every call, even one that changes nothing, moves the grid's revision on. A column's `type` and `slug` cannot change. `rows update` answers an empty object (printed as `{"status": null}`), not the new revision; read that from `grids get`.

---

## 4. API quirks (all real — keep these in mind)

- **Slugs are permanent in practice.** `pages move` can change one, but the old address answers 404 and links and magic-links to it break.
- **`--fields` REPLACES the default (`content`)**, it does not add to it. `--fields attributes` returns metadata only (no body); use `--fields content,attributes` to get both.
- **Content is not returned unless requested.** Without `fields=content` (the CLI default for `pages get`), the body is absent. When passing explicit `--fields`, include `content` if you need the body.
- **Valid `fields=` values are only:** `redirect, breadcrumbs, attributes, content, access_policy, access_lists, owner`. Passing `id`, `title`, or `slug` returns **400 BAD_REQUEST** (those are always-present default fields).
- **Search paging has no reliable end** — `next_cursor` is set even after an empty page; see §2 *Search*.
- **`GET /v1/pages/get-by-slug` returns 404** — the working form is `GET /v1/pages?slug={slug}` (what the CLI does).
- **`PATCH` returns 405** — always `POST` for updates (the CLI does this).
- **Strip YAML frontmatter before `--content`** — the CLI does not auto-strip it, nor auto-lift `title:`.
- **Never use `jq` on the `content` of WYSIWYG pages** — WYSIWYG content contains control characters that break `jq`. `jq` is fine for `id`/`slug`/`title` and for listing responses; use a Python parser for WYSIWYG `content`.

---

## 5. Tracker cross-linking (magic links)

Yandex Wiki and Tracker are integrated:

- **In a wiki page → Tracker:** type a bare issue key (e.g. `QUEUE-123`) anywhere in the body; it auto-renders as a Tracker card showing live status and title. No special syntax.
- **In a Tracker comment → Wiki:** paste the full URL, e.g. `https://wiki.yandex.ru/<your-space>/...`.

Note: a magic link always shows the issue's **current** status, so avoid magic-linking Draft/Unconfirmed issues from a published page (they read as unfinished).

---

## 6. Authoring YFM

Yandex Flavored Markdown supports note blocks, cuts/spoilers, tabs, multi-column layouts, tables, diagrams (Mermaid), and includes. See:

- `rules/02-content-standards.md` — which YFM element to use when (notes, cuts, tabs, layouts, tables, code blocks, diagrams) and when **not** to.
- `rules/03-include-usage.md` — the `{{include}}` element for DRY shared content.
- `rules/01-page-structure.md` — slug conventions and the page preamble (status note + updated date).

Full YFM syntax reference: the bundled [`references/yfm-quick-ref.md`](references/yfm-quick-ref.md), plus the live docs at <https://yandex.ru/support/wiki/>.
