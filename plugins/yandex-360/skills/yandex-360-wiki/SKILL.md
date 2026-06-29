---
name: yandex-360-wiki
description: Use when reading from or writing to Yandex Wiki via the ycli tool — fetch page content and metadata, walk the page tree with descendants/cursor pagination, list comments and attachments, or create/update pages with YFM body content through the CLI, MCP, or Python SDK. Covers the Wiki API's real quirks (permanent slugs, the fields= rules, no text-search endpoint, POST-not-PATCH).
category: workflow
---

# Yandex Wiki

Drive Yandex Wiki (Yandex 360) through `ycli`: read page content, metadata, tree, comments and attachments; create and update pages with YFM. This skill covers the CLI, the read-only MCP tools, the Python SDK, and the API's real-world quirks.

## When to use

- An agent needs context from the Wiki: read a page's content or metadata, walk a subtree, list comments or attachments.
- An agent needs to create or update a page with YFM content (notes, tabs, cuts, layouts, tables, diagrams, includes).

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

> Wiki uses the header `X-Org-Id` (capital `I`, lowercase `d`) — **different** from Tracker's `X-Org-ID`. This is a real gotcha; the CLI/SDK handle it for you, but watch for it in raw `http` calls.

**Three ways in:**

| Surface | What it covers |
|---------|----------------|
| **CLI** — `uv run ycli wiki <group> <cmd>` | Everything: `pages get\|create\|update\|descendants`, `comments list`, `attachments list` |
| **MCP tools** (read-only, 5) | `wiki_pages_get`, `wiki_pages_meta`, `wiki_pages_descendants`, `wiki_comments_list`, `wiki_attachments_list`. **No write tools** — `pages create` / `pages update` are CLI-only. |
| **Python SDK** | `from ycli.yandex.wiki.client import WikiClient` → `WikiClient(oauth_token=…, organization_id=…)` exposes `.pages` (`get`, `descendants`, `create`, `update`), `.comments` (`list`), `.attachments` (`list`). |

**Prefer the CLI / MCP tools over raw `http` calls** — they encode the API quirks (header name, `slug=` query form, POST-not-PATCH, `fields=` rules) correctly.

Full API reference: `../../../docs/references/yandex/wiki/`. Start at `../../../docs/references/yandex/wiki/index/docs.md` to find the right doc.

---

## 2. Reading

Every read is available both as a CLI command and as a read-only MCP tool.

| Operation | CLI command | MCP tool |
|-----------|-------------|----------|
| Full page content | `uv run ycli wiki pages get <slug>` | `wiki_pages_get` |
| Metadata only (id, title, owner, timestamps) | `uv run ycli wiki pages get <slug> --fields attributes` | `wiki_pages_meta` |
| Content **and** metadata in one call | `uv run ycli wiki pages get <slug> --fields content,attributes` | — |
| Descendant slugs (paginated) | `uv run ycli wiki pages descendants <slug> [--cursor C]` | `wiki_pages_descendants` |
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

### Tree navigation with cursor pagination

`pages descendants` returns one page of `{id, slug}` refs plus a `next_cursor`. Pass `next_cursor` back as `--cursor` to fetch the next page; repeat until there is no cursor.

```bash
uv run ycli wiki pages descendants team
uv run ycli wiki pages descendants team --cursor <next_cursor>   # subsequent pages
```

Use this to build a slug→title map of a subtree, then `pages get <slug> --fields attributes` per slug for titles.

### Comments and attachments — the 2-step get-id-then-list pattern

The comments/attachments endpoints key off the numeric page **id**, not the slug. So:

```bash
uv run ycli wiki pages get your-space/page    # → read the "id" field from the output
uv run ycli wiki comments list <page_id>
uv run ycli wiki attachments list <page_id>
```

### There is no API text-search endpoint

The Wiki UI has full-text search, but the **public API does not expose one** (see `../../../docs/references/yandex/wiki/04-navigation/search.md` — UI-only). To find a page programmatically, navigate the tree (`pages descendants` + `pages get`) from a known root, or use the Wiki UI search to locate the slug first, then fetch it via the CLI.

---

## 3. Writing

Writing is `pages create` / `pages update` (CLI-only — no MCP write tools). The simplest flow: author the page body in a local YFM file, then publish it.

### Before you write

- **Decide the slug first.** Slugs are **permanent after creation** — they cannot be changed, and changing them would break every inbound link and magic-link reference. Format: `parent/child`, kebab-case, no spaces, no underscores, no Cyrillic.
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

---

## 4. API quirks (all real — keep these in mind)

- **Slugs are permanent.** Never change a slug after creation — it breaks links and magic-links.
- **`--fields` REPLACES the default (`content`)**, it does not add to it. `--fields attributes` returns metadata only (no body); use `--fields content,attributes` to get both.
- **Content is not returned unless requested.** Without `fields=content` (the CLI default for `pages get`), the body is absent. When passing explicit `--fields`, include `content` if you need the body.
- **Valid `fields=` values are only:** `redirect, breadcrumbs, attributes, content, access_policy, access_lists, owner`. Passing `id`, `title`, or `slug` returns **400 BAD_REQUEST** (those are always-present default fields).
- **No API text-search endpoint** — navigate the tree or use the UI search (see §2).
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

Full YFM syntax reference: [`../../../docs/references/yandex/wiki/yfm-quick-ref.md`](../../../docs/references/yandex/wiki/yfm-quick-ref.md).
