# Full API coverage — design & implementation spec (2026-07-09)

## Goal / Definition of Done
`ycli` must expose **100% of the documented public REST API** for **Tracker, Wiki, Forms**
across the right surfaces, so every documented operation is doable via **MCP, CLI, or SDK**,
and everything (especially MCP, which agents consume) is **richly typed and metadata-enriched**.

Baseline at start (2026-07-09): **29 / ~225 endpoints wrapped (~13%)**.
- Tracker ~150 total, 17 wrapped, ~133 missing (~50 read / ~83 write)
- Wiki 42 total, 7 wrapped, 35 missing (11 read / 24 write)
- Forms 33 total, 5 wrapped, 28 missing (11 read / 17 write)

Full per-endpoint inventory: see the research captured in this session (scratchpad
`gap-inventory.md`) and the vendored docs `docs/references/yandex/{tracker/18-api,wiki/07-api,forms/09-api}`.

## Approved decisions (user, 2026-07-09)
1. **Delivery:** reach 100% in **waves with checkpoints**, all on branch `feat/full-api-coverage`,
   **no push to main / no auto-release**. Present between waves for review.
2. **Write bodies:** **fully-typed pydantic models for every request body**, including the 12
   polymorphic Forms question schemas (discriminated union), Tracker entities, Wiki grids, queue
   triggers. (Not the pragmatic JSON-body shortcut.)
3. **Metadata:** **maximum** — `Field(description=…)` on every model field (surfaces in MCP
   outputSchema), 2–4 sentence tool docstrings (what it returns / when to use vs siblings /
   gotchas), `Annotated[type, Field(description=…)]` on every MCP tool parameter, a call example
   in every MCP tool docstring, enriched domain-level `instructions` with a resource inventory,
   and cross-references between related tools.

## Surface rules (final)
- **Normal read** → SDK + CLI + MCP
- **Binary download** → SDK + CLI (NO MCP — base64 blobs to an agent are an anti-pattern; the
  matching *list* endpoint is a normal read and does go to MCP)
- **Write / action** → SDK + CLI (MCP is read-only, ARCH-3)
- **Async trigger** (export/clone/bulk) → SDK + CLI, plus a first-class `operations get` read on
  all three surfaces so agents can poll via MCP. Trigger CLI commands take `--wait/--no-wait`
  (default `--wait`: poll to terminal state; for export then download to `--output`).

## Exclusions (no public REST API — do NOT implement)
Tracker: `DELETE /issues/{key}`, `GET /issues` (list), `PATCH /queues/{id}` (phantoms); the
`index/` tree (navigation-only); reference/type pages (`projects/schemas.md`,
`triggers/{actions,conditions}.md`, `entities/{key-results,metrics}.md`).
Wiki: full-text search, page history/versions listing, ACL/roles (UI-only).
Forms: integration hooks/auto-actions (tracker/wiki/email/webhook/metrica/cloud-fn — UI/gateway only).

## Authoring standard (every resource follows this)
Scaffold: `python scripts/new_endpoint.py <domain> <resource>`, then wire.

- **client.py** (HTTP only, uplink; NO `from __future__ import annotations`): one method per
  endpoint. Read `@uplink.returns.json()`+`@uplink.get`; write `@uplink.returns.json()`+`@uplink.json`+verb+`body: uplink.Body`.
  Every method: `METHOD /path → …` docstring + `>>> … # doctest: +SKIP`. Pagination via a
  `ycli.yandex.pagination` strategy; public `list()` returns flat `XList`.
- **models.py** (`from __future__ import annotations`; inherit `APIModel`): flat public
  `XList(RootModel[list[X]])`, internal envelope `XResponse`. **Every field** carries
  `Field(description="…")`. Full, unabbreviated names. Class docstring + `>>>` doctest.
  Typed write-body IN-models (`XCreate`/`XUpdate`), discriminated unions where the API is polymorphic.
- **cli.py** (`from __future__`): `typer.Typer(name=…, no_args_is_help=True)` + `@app.callback()`.
  Reads/writes render via `Serializer.serialize(...)`; scalar `count` uses `print()`; binary uses
  the shared binary-output helper (`--output`). Every option a full `typer.Option(help=…)`.
- **mcp.py** (FastMCP, READ-ONLY): tools only for reads. Import `RO, TAGS, <domain>_client` from
  `<domain>.dependencies`. `@mcp.tool(name="<resource>_<verb>", annotations={**RO,"title":…}, tags=TAGS)`.
  Verb ∈ **{get, list, count, search, descendants, meta}** (a new verb ⇒ edit `READ_VERBS` in
  `tests/test_architecture.py` AND `ARCHITECTURE.md`, same PR). Docstring = description (never
  `description=`); return annotation = outputSchema (never `output_schema=`). Each param
  `Annotated[type, Field(description=…)]`. Max-metadata: 2–4 sentence docstring + a `>>>` example.

## New shared patterns (Wave 0 foundations — build first)
- **`ycli.yandex.polling`** — `poll(fetch, is_done, *, attempts, backoff, sleep=…)` injecting
  `sleep` for testability. Used by Tracker bulk, Wiki clone, Forms export.
- **Binary output helper** — CLI writes `bytes` to `--output PATH` or stdout buffer (ARCH-4
  carve-out, like `print(int)`). Client returns `bytes` (no `@uplink.returns.json()`).
- **Multipart upload** — uplink `@uplink.multipart` + `uplink.Part`; octet-stream via headers +
  raw `uplink.Body`.
- **Pagination strategies** — extend `pagination.py`: `OffsetStrategy` (Forms surveys, Tracker
  `perPage`/`page`), relative-cursor (`_relative`), `_paginate`; Tracker `_search` scroll stays
  in `issues`. Fix 3 latent single-page bugs: wiki `comments.list`, wiki `attachments.list`
  (→ `CursorStrategy`), forms `surveys.list` (→ `OffsetStrategy`).

## Wave plan
- **Wave 0 — foundations** (poller, binary helper, pagination strategies, 3 pagination-bug fixes) + spec.
- **Wave 1 — all reads** across SDK+CLI+MCP + the enrichment standard on new + touched code.
- **Wave 2 — high-value writes** (issue/comment/link/worklog/checklist CRUD; wiki page
  delete/restore/append/clone + comments; forms publish/unpublish + survey/question CRUD + export
  + keysets; tracker queues/fields/statuses/resolutions/boards/sprints CRUD).
- **Wave 3 — admin/niche** (tracker triggers/autoactions/webhook-logs/import/dashboards/entities
  full; wiki grids full CRUD + upload-sessions + binary; forms files/images/submit/suggest).
- **Final** — README per-domain coverage tables (sectioned by resource), update `docs/api-coverage.md`,
  ARCH-4 binary carve-out note, ARCHITECTURE/CLAUDE as needed.

## Parallelization model (conflict-free)
Implementation agents are **isolated resource-package producers**: each CREATES a new
`src/ycli/yandex/<domain>/<resource>/` package + a new `tests/yandex/<domain>/<resource>/` dir and
self-validates its `test_client.py` + `test_models.py` (+ MCP test against the resource subserver)
with `--no-cov`. Agents do **not** edit the shared domain `client.py`/`cli.py`/`mcp.py` or
snapshots. The **orchestrator** applies all wiring (register + mount), regenerates snapshots, runs
the full suite (100% coverage + ARCH + snapshots), fixes integration, checkpoint-commits, presents.

## Validation gates (mirror CI before every checkpoint)
`uv run ruff format --check .` · `uv run ruff check .` · `uv run lint-imports` · `uv run ty check`
· `uv run pytest` (100% cov + ARCH-1..11 + snapshots) · `uv lock --check`. Never write a skip-ci token.
