# Yandex 360 API Coverage

`ycli` now wraps the **near-complete public REST API** of Yandex 360 (Tracker, Wiki, Forms)
across all three surfaces. Every documented write and binary operation is reachable from the
**Python SDK** and the **CLI**; every documented read is additionally exposed as a read-only
**MCP** tool. This doc records the current coverage, the endpoints intentionally left out
(no public REST API — *not* gaps), and the handful of method signatures inferred from
truncated vendored docs.

The per-resource, per-operation breakdown lives in the README's
[Coverage section](../README.md#coverage), which is **generated from the live code** by
[`scripts/gen_coverage.py`](../scripts/gen_coverage.py) (introspects each domain client offline)
— run `uv run python scripts/gen_coverage.py --check` to confirm it is in sync.

**Design invariant:** the MCP server is intentionally **read-only** (ARCH-3). Throughout this
doc "no MCP write tool" is *by design*, never counted as a gap — writes live in the SDK/CLI only.

## Coverage at a glance

Verified **2026-07-09** (branch `feat/full-api-coverage`) by introspecting the domain clients
and cross-checking the vendored references (`references/yandex-360/{tracker,wiki,forms}/ru/api-ref`)
against the live official API. The counts below are the wrapped operations reported by the
generator, not estimates.

| Service | Resources | SDK + CLI operations | Read-only MCP tools | REST coverage |
|---------|-----------|----------------------|---------------------|---------------|
| **Tracker** | 32 | 153 | 57 | ~100% of the documented public API\* |
| **Wiki** | 9 | 43 | 13 | ~100% of the documented public API\* |
| **Forms** | 9 | 34 | 10 | ~100% of the documented public API\*† |
| **Total** | **50** | **230** | **80** | — |

> Authoritative per-operation counts live in the [README Coverage section](../README.md#coverage),
> generated from live code by `scripts/gen_coverage.py`; this glance table is a hand-verified snapshot.

\* Excludes the UI-only endpoints listed under [Intentional exclusions](#intentional-exclusions-not-gaps);
those have no public REST API.
† Two Forms endpoints ship with an **inferred** HTTP method/path — see
[Inferred signatures](#inferred-signatures-honest-caveats).

Baseline at the start of this work (2026-07-09): **29 / ~225 endpoints wrapped (~13%)** — Tracker
17, Wiki 7, Forms 5. The full-API-coverage effort closed the remaining gap in waves (reads →
high-value writes → admin/niche), each shipped across the surfaces its rule prescribes:

- **Normal read** → SDK + CLI + MCP
- **Binary download** → SDK + CLI (no MCP — base64 blobs to an agent are an anti-pattern; the
  matching *list* endpoint is a normal read and does go to MCP)
- **Write / action** → SDK + CLI (MCP is read-only, ARCH-3)
- **Async trigger** (export / clone / bulk) → SDK + CLI, plus a first-class `operations get` read
  on all three surfaces so agents can poll via MCP

## Intentional exclusions (not gaps)

These have **no public REST API** and are deliberately not implemented. They are UI/gateway-only
or navigation-only doc artifacts, and must not be inferred into endpoints.

**Tracker**
- `DELETE /issues/{key}`, `GET /issues` (bulk list) and `PATCH /queues/{id}` — **phantom** paths
  that appear only in the navigation-only `index/` tree, not in the authoritative `18-api/`.
- The `index/` tree (navigation-only) and the reference/type pages (`projects/schemas.md`,
  `triggers/{actions,conditions}.md`, `entities/{key-results,metrics}.md`) describe payload
  shapes, not callable endpoints.

**Wiki**
- Full-text search, page history / versions listing, and ACL / role management — all UI-only.

**Forms**
- Integration **hooks / auto-actions** (Tracker / Wiki / email / webhook / Metrica / cloud-function)
  — configured in the Forms UI / gateway only.
- Single-answer **`GET .../answers/{id}`** — no deployed route on any API version (every path
  variant returns a server 404, confirmed by live E2E); the `answers.get` op was removed. Read a
  single answer via `answers.list` / `answers.list_all`.

## Inferred signatures (honest caveats)

Two Forms endpoints were implemented from **truncated** vendored docs, so their HTTP
method + path follow REST convention and the `03-forms/index.md` labels rather than a verbatim
request line. Both caveats are also recorded in the client docstrings
(`src/ycli/yandex/forms/surveys/client.py`):

- `surveys.create` → **`POST /surveys`** — `03-forms/create.md` shows only the request body
  (the request line was truncated); `03-forms/index.md` lists it as "Create form".
- `surveys.modify` → **`PATCH /surveys/{id}`** — `03-forms/modify.md` shows only the request body;
  `03-forms/index.md` lists it as "Modify form".

Everything else is confirmed against the vendored references and the live official API.

---

*Sources: offline introspection of `src/ycli/yandex/**` via `scripts/gen_coverage.py`; vendored
docs `references/yandex-360/**` (Tracker/Wiki/Forms `ru/api-ref/`); live
official references at yandex.ru/support/{tracker,wiki,forms}/…/api-ref (verified 2026-07-09).*
