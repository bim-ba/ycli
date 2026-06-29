# Yandex 360 API Coverage — gap analysis & roadmap

Status of `ycli`'s coverage of the Yandex 360 REST APIs (Tracker, Wiki, Forms) across all
three surfaces (Python SDK, CLI, MCP), with a prioritized roadmap. Derived from a source
audit of `src/ycli/yandex/**` cross-checked against the vendored docs in
`docs/references/yandex/**` and the current official API references (2026-06).

**Design invariant:** the MCP server is intentionally **read-only**. Throughout this doc,
"no MCP write tool" is *by design*, never counted as a gap. Writes live in the SDK/CLI only.

## Coverage at a glance

Verified 2026-06-27 by a per-service source audit cross-checked against the live official API
(supersedes the earlier estimates — endpoint counts were inflated by the navigation-only `index/`
trees, now corrected to the authoritative `18-api/` / `07-api/` / `09-api/` figures).

| Service | Public endpoints | Wrapped | Read coverage | Write coverage |
|---------|------------------|---------|---------------|----------------|
| **Tracker** | ~152 | 16 | ~17% | ~6% (issue create/update, comment add, link add, transition execute) |
| **Wiki** | 39 | 6 | ~25% | ~9% (`pages create`/`update` only) |
| **Forms** | 31 | 5 | ~28% | **0%** — entirely absent (public API supports it) |
| **Total** | **~222** | **27** | — | **≈12% overall** |

## Cross-cutting findings (act on these first)

1. **🐞 ✅ FIXED (2026-06-27) — Forms `answers list` ignored pagination.** It returned only the
   first page; the API paginates via `next.next_url`. Now `AnswersClient.list_all` follows the
   `next_url` cursor verbatim until exhausted, and the CLI (`forms answers list`) + MCP
   (`answers_list`) call it — draining every page. Covered by tests across all three surfaces.
2. **📄 ✅ RECONCILED (2026-06-27) — `index/` described phantom endpoints.** Both
   `docs/references/yandex/{tracker,wiki}/index/docs.md` now carry a prominent warning banner
   naming the authoritative dir (`18-api/` / `07-api/`) and listing every confirmed phantom/wrong
   path (e.g. Tracker has **no** `DELETE /v3/issues/{key}`; Wiki has no `PATCH /pages/{id}`,
   `/move`, `/history`, `/search`). Treat `index/` as navigation-only; never implement from it.
3. **🔑 ✅ VERIFIED (2026-06-27) — Write auth header is sent.** `Transport.session` sets a single
   canonical `X-Org-Id` header on the session for **every** request, writes included
   (case-insensitive per RFC 9110 → serves Tracker's `X-Org-ID` too). No change needed; the
   `forms:write` OAuth scope is a token-provisioning concern, not a code gap.
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
| ~~**🐞 Fix first**~~ ✅ done | answers pagination (follow `next.next_url`) | SDK+CLI+MCP | Correctness — was returning page 1 only; `list_all` now drains all pages |
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
  `index/` docs to `07-api/`; verify the org/write auth header in `Transport.session`.
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
