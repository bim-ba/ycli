# Yandex 360 API Coverage — gap analysis & roadmap

Status of `ycli`'s coverage of the Yandex 360 REST APIs (Tracker, Wiki, Forms) across all
three surfaces (Python SDK, CLI, MCP), with a prioritized roadmap. Derived from a source
audit of `src/ycli/yandex/**` cross-checked against the vendored docs in
`docs/references/yandex/**` and the current official API references (2026-06).

**Design invariant:** the MCP server is intentionally **read-only**. Throughout this doc,
"no MCP write tool" is *by design*, never counted as a gap. Writes live in the SDK/CLI only.

## Coverage at a glance

| Service | Resource families | Endpoints wrapped | Read coverage | Write coverage |
|---------|-------------------|-------------------|---------------|----------------|
| **Tracker** | 9 / ~25 (~35%) | ~10 | issue-centric path solid; org-level absent (~40–45%) | minimal (~15–20%): issue create/update, comment add, link add, transition execute |
| **Wiki** | 3 / ~9 (~33%) | ~7 / ~35 (~20%) | common path solid; gaps remain | `pages create`/`update` only |
| **Forms** | 4 / 9 (~44%) | 5 / ~30 (~17%) | ~36% (no pagination, no single-item gets) | **0%** — entirely absent (public API supports it) |

## Cross-cutting findings (act on these first)

1. **🐞 Bug — Forms `answers list` ignores pagination.** It returns only the first page; the
   API paginates via `next.next_url`. Today `ycli forms answers list <id>` silently under-reports
   responses. This is a correctness bug, not just a missing feature. **Fix first.**
2. **📄 Docs rot — Wiki `index/` describes phantom endpoints.** `docs/references/yandex/wiki/index/docs.md`
   (and `index/endpoints/*`) list endpoints that do **not** exist in the real v1 API
   (`PATCH /pages/{id}`, `/pages/{id}/move`, `/pages/{id}/history`, `/pages/search`, a `/restore`
   path, `upload-session` paths). The authoritative source is `07-api/`, which the current code
   already matches (e.g. update is `POST /pages/{id}`). **Reconcile `index/` to `07-api/`** so we
   never implement a phantom endpoint.
3. **🔑 Write auth header.** Adding writes (esp. Forms) needs the `forms:write` scope and the org
   header. Verify `src/ycli/yandex/base.py::session_from_env` sends the org header on the write
   path before implementing Forms/Wiki write expansion.
4. **Read-only MCP stays read-only.** Any new write endpoint goes to SDK + CLI only; never add an
   MCP write tool.

## Tracker — roadmap

**Covered:** issues (get/full/search/count/create/update), comments (list/add), links (list/add),
transitions (list/execute), worklog (list), changelog, priorities, issuetypes, linktypes.

| Tier | Capability | Surfaces | Why |
|------|-----------|----------|-----|
| **Quick win (read)** | `queues` list/get | SDK+CLI+MCP | Agents can't enumerate queues today — foundational discovery |
| **Quick win (read)** | global `fields/` + queue `localFields` | SDK+CLI+MCP | Discover/interpret custom field IDs for create/update |
| **Quick win (read)** | `users/` + `myself` | SDK+CLI+MCP | Resolve assignee logins (issue payloads lack `login`); whoami |
| **Quick win (read)** | `statuses` + `resolutions` dictionaries | SDK+CLI+MCP | Siblings of the already-covered priorities/issuetypes; validate transition/resolution values |
| **Quick win (read)** | saved `filters/` | SDK+CLI+MCP | Reuse org-defined searches |
| **Quick win (read)** | cross-issue `worklog/_search` | SDK+CLI+MCP | Worklog reporting across issues |
| **Medium** | checklists (`checklistItems` CRUD) | read MCP + write CLI | Task breakdown; common agent op |
| **Medium** | bulk update/move + status poll (`bulkchange`) | CLI + read status | One async call vs N PATCHes; rate-limit friendly |
| **Medium** | boards & sprints (list/get; sprint start/archive) | read MCP + write CLI | Agile-aware agents |
| **Medium** | comment edit/delete + reactions; link delete; worklog add/edit; issue delete/move | CLI | Round out existing resources |
| **Large** | attachments (list/download read; upload write) | read MCP + write CLI | Read attached specs/logs; upload is multipart |
| **Large** | Entities API (projects/portfolios/goals + sub-tree) | SDK+CLI | New entity surface |
| **Large** | automation (triggers/macros/autoactions), import, webhooks | SDK+CLI | Niche / elevated perms |

> Note: `changelog` is wrapped at `GET issues/{key}/changelog`; official docs also call this
> the issue *history* resource — confirm the exact path is still served.

## Wiki — roadmap

**Covered:** pages (get-by-slug/descendants/create/update), comments (list), attachments (list).

| Tier | Capability | Surfaces | Why |
|------|-----------|----------|-----|
| **Quick win** | page `DELETE` (returns `recovery_token`) + restore-by-token | CLI | Core lifecycle; safe-by-design |
| **Quick win** | comment create (+ delete) | CLI | Programmatic feedback |
| **Quick win** | append-content (`POST /pages/{id}/append-content`) | CLI | Append-only edits avoid read-modify-write races — natural "agent adds a section" |
| **Quick win (read)** | get page by id (`GET /pages/{id}`) | SDK+CLI+MCP | Avoids a slug round-trip when only id is known |
| **Quick win (read)** | attachment download (by id / slug+filename) | SDK+CLI | Today you can list but not fetch bytes |
| **Quick win (read)** | `users/me` | SDK+CLI+MCP | whoami / auth sanity |
| **Medium** | page clone/copy + Operations poller | CLI | Template-driven page duplication (async) |
| **Medium** | page-resources listing (unified attachments+grids, sort/search) | SDK+CLI+MCP | Richer page inspection |
| **Large** | attachment upload (upload-session pipeline + attach) | CLI | Multi-step session + raw-binary |
| **Large** | Grids (dynamic tables) — grid/row/column/cell CRUD | SDK+CLI | Only if dynamic-table workflows are in scope |

> Not gaps (no public API): full-text search, page history/versions, ACL/access management — all
> UI-only. Do not implement.

## Forms — roadmap

**Covered (read-only today):** `users/me`, surveys (list/get), questions (list), answers (list).

| Tier | Capability | Surfaces | Why |
|------|-----------|----------|-----|
| **🐞 Fix first** | answers pagination (follow `next.next_url`) | SDK+CLI+MCP | Correctness — current list returns page 1 only |
| **Quick win** | publish / unpublish survey | CLI | The flagship "automate forms" use-case; single call, no body |
| **Quick win (read)** | get single question / get single answer | SDK+CLI+MCP | Round out reads; MCP-safe |
| **Medium** | answer export + Operations poll (`export` → `operations/{id}` → `export-results`) | CLI | The real way to pull all responses as xlsx/csv |
| **Medium** | survey CRUD (`POST`/`PATCH`/`DELETE`) | CLI | Programmatic form provisioning (large body schema) |
| **Medium** | keysets (create + download) | CLI | Personal-link generation |
| **Medium** | submit response (`POST .../form`); file/image upload | CLI | Automation/testing; question images |
| **Large** | question CRUD + move (~15 type-specific schemas) | CLI | Build a form end-to-end; biggest modeling cost |

> Not gaps (no public API): integration **hooks/auto-actions** (Tracker/Wiki/email/webhook/Metrica)
> are configured in the Forms UI/gateway only.

## Recommended phased plan

- **Phase 0 — correctness & hygiene (small):** fix Forms answers pagination; reconcile the Wiki
  `index/` docs to `07-api/`; verify the org/write auth header in `session_from_env`.
- **Phase 1 — read quick-wins (high ROI, mirrors the `priorities list` pattern):** Tracker
  queues / fields / localFields / users / myself / statuses / resolutions / filters; Wiki
  get-by-id / users-me / attachment download; Forms single-question / single-answer. Each is one
  uplink method + a CLI `list`/`get` + (reads) one RO MCP tool.
- **Phase 2 — high-value writes:** Wiki page delete (+restore), comment create, append-content;
  Forms publish/unpublish; Tracker checklists. Then Forms answer export (+ Operations poller).
- **Phase 3 — larger surfaces (scope on demand):** Tracker bulk ops, boards/sprints, attachments
  upload; Forms survey/question CRUD; Wiki clone/copy, attachment upload, Grids; Tracker Entities.

Every new read endpoint should ship across SDK+CLI+MCP; every write across SDK+CLI only, with a
test per surface (TDD), keeping the suite at 100% coverage.

---

*Sources: source audit of `src/ycli/yandex/**`; vendored docs `docs/references/yandex/**`
(Tracker `18-api/`, Wiki `07-api/`, Forms `09-api/`); live official references at
yandex.ru/support/{tracker,wiki,forms}/…/api-ref (verified 2026-06).*
