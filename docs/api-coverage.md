# Yandex 360 API Coverage

`ycli` wraps the bulk of the public REST API of Yandex 360 (Tracker, Wiki, Forms) across
all three surfaces. Every wrapped operation is reachable from the **Python SDK** and the
**CLI**; the **MCP** server mirrors both reads and writes with honest annotations (reads
carry `readOnlyHint=True`; writes carry `readOnlyHint=False` plus explicit
`destructiveHint`/`idempotentHint`), and `ycli mcp start --read-only` serves the
reads-only view. This doc records the current coverage, the endpoints intentionally left
out (no public REST API — *not* gaps), and the documented endpoints not yet wrapped
(honest gaps).

The per-resource, per-operation breakdown lives in the README's
[Coverage section](../README.md#coverage), which is **generated from the live code** by
[`scripts/gen_coverage.py`](../scripts/gen_coverage.py) (introspects each domain client offline)
— run `uv run python scripts/gen_coverage.py --check` to confirm it is in sync.

**Design invariant:** the MCP server is read/write with **annotation honesty** (ARCH-3):
every tool's verb classifies fail-closed as READ / WRITE / WRITE_IDEMPOTENT / DESTRUCTIVE
and its hints must match the class exactly (`tests/test_architecture.py`). Throughout this
doc "no MCP tool" appears only for **binary payloads** — raw-bytes downloads are CLI/SDK-only
by design, never counted as a gap.

## Coverage at a glance

Verified **2026-07-12** (branch `feat/mcp-read-write`) by introspecting the domain clients,
cross-checking the vendored references (`references/yandex-360/{tracker,wiki,forms}/ru/api-ref`,
re-fetched 2026-07-10), and a **full-surface live test of all 230 SDK operations** against a
real org (see [`docs/e2e-findings.md`](e2e-findings.md)). The counts below are the wrapped
operations reported by the generator, not estimates.

| Service | Resources | SDK + CLI operations | MCP tools | Documented endpoints not yet wrapped |
|---------|-----------|----------------------|-----------|--------------------------------------|
| **Tracker** | 32 | 153 | 151 | 13 |
| **Wiki** | 9 | 43 | 42 | 5 |
| **Forms** | 9 | 35 | 28 | 24 |
| **Total** | **50** | **231** | **221** (+`status_get` = 222) | **42** |

> Authoritative per-operation counts live in the [README Coverage section](../README.md#coverage),
> generated from live code by `scripts/gen_coverage.py`; this glance table is a hand-verified snapshot.

Baseline at the start of this work (2026-07-09): **29 / ~225 endpoints wrapped (~13%)** — Tracker
17, Wiki 7, Forms 5. The full-API-coverage effort closed most of the gap in waves (reads →
high-value writes → admin/niche); the MCP read/write change (2026-07-12) then mirrored the whole
SDK onto MCP. Each operation ships across the surfaces its rule prescribes:

- **Normal read** → SDK + CLI + MCP (`readOnlyHint=True`)
- **Write / action** → SDK + CLI + MCP (`readOnlyHint=False` + explicit
  `destructiveHint`/`idempotentHint`; every write tool carries the `write` tag that
  `--read-only` disables)
- **Binary download** → SDK + CLI only (raw bytes to an agent are an anti-pattern; the
  matching *list* endpoint is a normal read and does go to MCP)
- **Binary upload** → SDK + CLI; the Wiki attachment upload additionally ships as MCP tools
  taking base64 input (`wiki_attachments_upload`, the `wiki_uploadsessions_*` pipeline)
- **Async trigger** (export / clone / bulk) → all three surfaces, plus a first-class
  `operations get` read so agents can poll

## Known gaps (documented, not yet implemented)

The 2026-07-12 coverage-gap audit (vendored docs re-fetched 2026-07-10, one day after the
previous verification) found **43 documented public endpoints** that ycli did not wrap; one
(the Forms single-answer view) has since been implemented on this branch, leaving **42**.
These are honest gaps — candidates for `/new-endpoint` — not exclusions:

**Tracker (13)**
- **Issue attachment writes (3):** `POST /v3/issues/{id}/attachments/` (upload onto an issue),
  `POST /v3/attachments/` (temp upload — the missing producer of the `temp_file_id` that the
  already-wrapped `entities.attachments_attach` requires, making that op a dead end today),
  `DELETE /v3/issues/{id}/attachments/{file_id}`.
- **Projects API v3 (6):** full CRUD on `/v3/projects` (`GET` list/one/queues, `POST`, `PUT`,
  `DELETE`) — the newer *entities* API overlaps but does not replace these routes.
- **Permission reads (4):** `GET /v3/queues/{id}/permissions/{users,groups}/…` and the
  component twins — natural MCP reads; ycli has the *write* (`queues.set_permissions`) but
  cannot read back what it set.

**Wiki (5)**
- **Page ACL management (4):** `POST|DELETE /v1/pages/{idx}/access[/{access_id}]`
  (`pages_access/` in the current api-ref).
- **Server-side comment thread (1):** `GET /v1/pages/{idx}/comments/{comment_id}/thread` —
  ycli's `comments thread` currently reconstructs the thread client-side.

**Forms (24)**
- **Integration hooks (17):** hook groups, subscriptions (actions), conditions, and template
  variables on `api.forms.yandex.net/v1/surveys/{id}/hooks…` — the form→Tracker/Wiki/mail/webhook
  automation surface.
- **Notification history (5):** `GET /v1/notifications[/{id}[/status]]`,
  `POST /v1/notifications/{id}/{cancel,restart}`.
- **Answer integrations view (1):** `GET /v1/answers/integrations`. (The single-answer view
  `GET /v1/answers?answer_id=…` was **live-verified deployed** — HTTP 200 — and is now wrapped
  on this branch as `answers get` / `forms_answers_get`, so it left this list.)
- **Diagnostics (1):** `GET /v1/surveys/{id}/show-errors`.

## Intentional exclusions (not gaps)

These have **no public REST API** and are deliberately not implemented. They are UI-only or
navigation-only doc artifacts, and must not be inferred into endpoints.

**Tracker**
- `DELETE /issues/{key}`, `GET /issues` (bulk list) and `PATCH /queues/{id}` — **phantom** paths
  that appear only in the navigation-only `index/` tree, not in the authoritative `18-api/`.
- The `index/` tree (navigation-only) and the reference/type pages
  (`triggers/{actions,conditions}.md`, `entities/{key-results,metrics}.md`) describe payload
  shapes, not callable endpoints.

**Wiki**
- Full-text search and page history / versions listing — UI-only. (Page **ACL management** is
  *not* on this list anymore: the current api-ref documents it — see Known gaps.)

**Forms**
- Appearance / themes and analytics / charts — UI-only. (Integration **hooks** are *not* on this
  list anymore: the current api-ref documents them on `api.forms.yandex.net/v1` — see Known gaps.
  Likewise the single-answer `GET /v1/answers?answer_id=…` route is deployed and live-verified.)

## Retired caveats

- **Forms inferred signatures — resolved.** `surveys.create` (`POST /surveys`) and
  `surveys.modify` (`PATCH /surveys/{survey_id}`) were originally implemented from truncated
  vendored docs; the current api-ref carries full request lines and the 2026-07-10/12 live E2E
  runs confirmed both. The signatures are no longer inferred.

---

*Sources: offline introspection of `src/ycli/yandex/**` via `scripts/gen_coverage.py`; the MCP
tool snapshot `tests/snapshots/mcp_tools.txt`; vendored docs `references/yandex-360/**`
(Tracker/Wiki/Forms `ru/api-ref/`, re-fetched 2026-07-10); live official references at
yandex.ru/support/{tracker,wiki,forms}/…/api-ref; full-surface live test against a real org
(2026-07-12, see `docs/e2e-findings.md`).*
