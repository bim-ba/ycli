# Round-4 Architecture Refactor — Design

**Status:** approved decisions, pending user review of this spec
**Branch:** `refactor/round-4-architecture` (off `main` @ v0.8.1)
**Date:** 2026-06-29

## Goal

Close the architecture debt surfaced in review points 3–7 plus a demo-reproducibility
smell: drop the one-off `RawMapping`/`full` raw accessor, turn the two cross-cutting
modules (`status`, `mcp`) into proper packages with the missing surfaces, tighten
pagination types, sweep small smells, and make the demo GIF render real CLI output from
committed fixtures instead of hand-typed `cat <<OUT` blocks.

## Architecture

Seven independent workstreams (W-A … W-G), each shippable and testable on its own. Every
public-surface change regenerates the `tests/snapshots/` files on purpose (ARCH-6); every
invariant edit changes `ARCHITECTURE.md` **and** its enforcing check in `tests/test_architecture.py`
in the same change (the repo's standing rule). The 100% coverage gate stays green
throughout — dead code is removed together with its now-dead tests.

## Tech Stack

Python ≥3.12 · uv · uplink+requests · typer · fastmcp (read-only) · pydantic v2 · ruff · ty ·
pytest + `responses` (HTTP stubbing) · vhs (demo GIF).

## Global Constraints

- `client.py` / `_base.py` modules MUST NOT use `from __future__ import annotations` (uplink reads
  runtime annotations). New non-client modules may use it.
- Credentials enter only at a composition root (`Credentials()`/`AppConfig()` for CLI, `_deps`
  factory for MCP) as raw `oauth_token`/`organization_id` constructor args. No `from_env`. Never
  hardcode `YANDEX_ID_*` (ARCH-5/7/8).
- MCP stays read-only (ARCH-3): every new tool's verb is in the read allow-list and carries
  `readOnlyHint=True` via `RO`.
- Self-documenting names, no abbreviations (e.g. `timeout_seconds`, not `timeout_s`).
- Output only via `output.Serializer.serialize(...)` (ARCH-4).
- 100% coverage (`--cov-fail-under=100`). Branch → PR → explicit approval; no direct push to main.
- No skip-ci token in any commit/squash message.

---

## W-A — Remove `RawMapping` / `full` / `get_raw` (point 3)

**Decision:** delete the raw unpruned accessor entirely; every resource is a typed model.

**Current state:**
- `RawMapping(RootModel[dict[str, Any]])` in `src/ycli/yandex/models.py:21` — used in exactly one place.
- `IssuesClient.get_raw` in `src/ycli/yandex/tracker/issues/client.py:29`.
- CLI `full` command in `src/ycli/yandex/tracker/issues/cli.py:30` (wraps the dict in `RawMapping`).
- MCP tool `issues_full` in `src/ycli/yandex/tracker/issues/mcp.py:32`.
- `"full"` listed in `READ_VERBS` (`tests/test_architecture.py:24`) and in the ARCH-3 allow-list text.
- ARCH-4 closes with the `RawMapping`-wrapping sentence (`ARCHITECTURE.md:47-48`).
- `docs/conventions/resources.md` §4 documents the `_raw`/`full` pattern.

**Target:** none of the above exists.

**Files:**
- Delete: `RawMapping` class (`models.py`), `get_raw` (`issues/client.py`), `full` command
  (`issues/cli.py`), `issues_full` tool (`issues/mcp.py`).
- Edit `ARCHITECTURE.md`: drop the ARCH-4 `RawMapping` sentence; remove `full` from the ARCH-3
  read-verb allow-list.
- Edit `tests/test_architecture.py`: remove `"full"` from `READ_VERBS`.
- Edit `docs/conventions/resources.md`: delete §4 (renumber following sections).
- Regenerate `tests/snapshots/mcp_tools.txt` (drops `tracker_issues_full`) via `/snapshot-regen`.
- Delete now-dead tests: `test_get_raw_returns_dict` (`test_client.py`), `test_issues_full_tool_*`
  (`test_mcp.py`), the two `full` CLI tests (`test_cli.py`), and the `issues_full` membership
  assertions in `tracker/test_mcp.py` and `issues/test_mcp.py`.

**Risk:** removing a public CLI command + MCP tool is a **breaking** public-surface change.
Reflect that in the release (see Release).

---

## W-B — `status` → package, simplify to native `me`, add MCP (points 4 + 7)

**Decision:** explode `src/ycli/yandex/status.py` into a `yandex/status/` package; drop the
`ServiceProbe` abstraction and the per-service identity lambdas; the report carries each service's
**bare native `me` object**; expose a read-only MCP tool `status_get` in a new `status` namespace.

**Current state:** `status.py` is a single module mixing models (`ServiceAuthStatus`, `AuthReport`),
a `ServiceProbe` class, a `PROBES` list with identity lambdas (`me.login` / `me.username` /
`me.email`), and the `auth status` Typer command. No MCP surface.

**Target package `src/ycli/yandex/status/`:**
- `__init__.py` — docstring; re-export `app` so `from ycli.yandex.status import app` (used in
  `cli.py:18`) keeps working unchanged.
- `models.py` — `ServiceAuthStatus` and `AuthReport`. `ServiceAuthStatus.identity: str | None`
  is **replaced** by a `me` field carrying the service's native `me` payload (point 7 — "just
  the `me` object"). The three services return **different** `me` models (Tracker `me.login`,
  Wiki `me.username`, Forms `me.email`), so the field is typed as the union
  `me: TrackerMe | WikiMe | FormsMe | None` (imported from each domain's `me/models.py`; models
  importing models breaks no ARCH rule). Keep `service`, `valid`, `detail` (operationally useful:
  the point of `auth status` is verifying the token actually works per service). The Serializer
  renders the nested model natively. *Confirm at plan time:* if pydantic union-discrimination on
  these shapes proves noisy, fall back to `me: dict | None` populated from `model_dump()`.
- `cli.py` — the `auth` Typer app + `status` command. Probe each service inline (build client via
  `ClientFactory`, call `client.me.get()`, attach the returned `me` model); no `ServiceProbe`
  class, no identity lambdas.
- `client.py` — none needed; status reuses each domain's existing `me` client. (Confirm whether a
  thin `StatusClient` aggregator improves testability; default is no new client.)
- `mcp.py` — read-only tool `status_get` (verb `get`, already in the allow-list; `readOnlyHint`
  via `RO`), returning the `AuthReport`. Wire its `_deps` per the MCP composition pattern.

**Wiring / back-compat:**
- `ycli auth status` CLI path stays identical.
- Mount the status MCP subserver in `ycli/mcp/__init__.py` with `namespace="status"` →
  tool name `status_get`.

**ARCH impact:**
- ARCH-1 ("four-surface symmetry") is scoped to `yandex/<domain>/<resource>/` dirs. `yandex/status/`
  is a domain with **no resource subdirectory**, so the letter does not bind it — but confirm the
  enforcing test's glob does not treat `yandex/status/` as a resource missing surfaces. If it does,
  add an explicit carve-out in `ARCHITECTURE.md` + the test naming `status` as a cross-cutting
  domain (client-less, resource-less).

**Tests:** model shape (`me` populated on success, `None` + `detail` on auth failure), CLI exit
codes (1 when unconfigured / any service invalid), MCP `status_get` read-only + returns report.
Snapshots gain `status_get`.

---

## W-C — `mcp` → package (`ycli/mcp/`) (point 4)

**Decision:** turn the two root MCP modules into a package; keep both public import paths.

**Current state:** `src/ycli/mcp.py` (root FastMCP server: `mcp` + `main`) and `src/ycli/mcp_cli.py`
(the `ycli mcp` Typer sub-app: `start`, `methods`).

**Target package `src/ycli/mcp/`:**
- `__init__.py` ← former `mcp.py`. Keeps `from ycli.mcp import main, mcp` working (the console
  entry point and `mcp_cli`'s lazy import both rely on these). Mounts wiki/tracker/forms **and**
  the new `status` subserver (W-B).
- `cli.py` ← former `mcp_cli.py` (the `mcp` Typer app). Update `cli.py:14` import from
  `ycli.mcp_cli` → `ycli.mcp.cli`.
- `__main__.py` — `from ycli.mcp import main; main()` so `python -m ycli.mcp` (documented in the
  server docstring) still runs the server now that `mcp` is a package, not a module.

**ARCH impact (carve-out required):**
- ARCH-3 says `fastmcp` is imported only in modules **named `mcp.py`**. The server now lives in
  `ycli/mcp/__init__.py`. Edit ARCH-3 text + its enforcing check to allow `fastmcp` in
  `ycli/mcp/__init__.py` (the package initializer of the `mcp` package) in addition to `mcp.py`
  modules. Same change to the import-linter contract if it pins module names.

**Tests:** `from ycli.mcp import main, mcp` resolves; `python -m ycli.mcp` entry exists;
`ycli mcp start` / `ycli mcp methods` unchanged. The smoke test (`registered_groups` `mcp` check)
stays valid.

---

## W-D — Pagination typing + Envelope protocol (point 6)

**Decision:** add PEP 695 generics + a typed page `Envelope` protocol; fold the free
`collect_single_page` function into the class hierarchy (OOP-encapsulation preference).

**Current state:** `src/ycli/yandex/pagination.py` — ABC strategies returning untyped `list`,
`Callable[[Any], Any]` page accessors, `cursor: Any`, and a module-level `collect_single_page`
free function.

**Target:**
- `PaginationStrategy[T]` generic; `collect(...) -> list[T]`.
- An `Envelope[T]` `Protocol` (or typed `Callable` aliases) describing the page-access surface:
  `extract: Callable[[E], list[T]]`, `next_of: Callable[[P], str | None]`,
  `next_url_of: Callable[[P], str | None]`, `fetch_url: Callable[[str], P]`.
- Replace `cursor: Any = None` with a typed cursor; `if cursor is None` / `if url is None` checks
  instead of truthiness where a typed `str | None` makes it precise.
- Fold `collect_single_page` into `SinglePageStrategy` (e.g. a classmethod/`collect_wrapped`)
  so the wiki/forms call sites use the class, not a free function.
- Remove `Any`/`ty: ignore` that the generics make unnecessary; use `@overload` where ty supports it.

**Constraint:** `pagination.py` is not a `client.py`, so `from __future__ import annotations` stays
fine; PEP 695 `type`/`class C[T]` syntax needs no future import.

**Tests:** existing pagination tests stay green; add a type-level assertion only if cheap. Behavior
is unchanged — this is a typing/encapsulation refactor.

---

## W-E — Smell sweep (point 5)

**Decisions (from review):**
- The 4 empty `__init__.py` (`yandex/__init__.py`, `wiki/attachments`, `wiki/comments`,
  `wiki/pages`) get **docstrings**, not deletion — ARCH-1 requires the files to exist.
- Move the in-body `import yaml` to module top in `tests/yandex/tracker/issues/test_cli.py`.
- `collect_single_page` free function → handled in W-D.
- `ServiceProbe` god-ish indirection → removed in W-B.

**Out of scope:** `_deps.py` per-domain boilerplate stays (intentional pattern, not a smell).

**Tests:** none new; the sweep must not change behavior or coverage.

---

## W-F — ARCHITECTURE docs + snapshots + drift gate

Consolidation workstream — every invariant edit lands with its enforcing check:
- ARCH-4: drop the `RawMapping` sentence (W-A).
- ARCH-3: drop `full` from the read-verb allow-list (W-A); add the `ycli/mcp/__init__.py` fastmcp
  carve-out (W-C).
- ARCH-1: status carve-out if the test glob requires it (W-B).
- `docs/conventions/resources.md`: delete §4 (W-A).
- Regenerate `tests/snapshots/` (CLI tree gains nothing/loses `full`; MCP list loses
  `tracker_issues_full`, gains `status_get`).
- Run the ARCH-11 doc-drift guard + full `uv run pytest` gate.

---

## W-G — Reproducible demo output (new)

**Decision:** variant **B** — render real CLI output from committed fixtures via in-process
`responses`; derive the MCP tool list from the live `ycli mcp methods`. No hand-typed output.

**Proven smell:** `docs/demo/bin/ycli` bakes a `cat <<OUT` tool list of **8** tools; the real server
registers **24** (`tests/snapshots/mcp_tools.txt`) — and the baked list both omits 16 real tools and
names `tracker_issues_full`, which W-A deletes. The two data commands (`tracker issues get`,
`wiki pages get`) are hand-authored sample text.

**Why not live creds:** would leak real org data into a public committed GIF, be non-deterministic
(API changes each regeneration), and require creds + network to regenerate (today it is offline).
Fixture-rendered output is real, deterministic, leak-free, and offline-regenerable — matching the
project's "generated from a committed source" value.

**Target:**
- `docs/demo/fixtures/*.json` — committed raw API response bodies (fake but realistic, leak-free;
  may be lifted from existing test fixtures).
- `docs/demo/render.py` — sets dummy env creds (`YANDEX_ID_OAUTH_TOKEN=demo`,
  `YANDEX_ID_ORGANIZATION_ID=demo`), registers the matching fixture with `responses`, invokes the
  **real** `ycli` Typer app in-process (`typer.testing.CliRunner`, the same mechanism the CLI tests
  use), and prints captured stdout. Output is genuine rendering of committed data.
- `docs/demo/bin/ycli` shim: replace the two `cat <<OUT` data branches with
  `exec uv run python docs/demo/render.py <args>`; replace the baked `mcp start` tool list with the
  real `ycli mcp methods` output (no creds/network; requires the `[mcp]` extra at regeneration —
  document in the tape header).
- `docs/demo/demo.tape`: adjust the `mcp` step to show real `ycli mcp methods`; retune
  Sleep/Height if the 24-tool list needs it.

**Tests:** `render.py` is demo tooling, not shipped in the dist. Add a lightweight test that
`render.py <known cmd>` exits 0 and emits the fixture's key field, so the demo can't silently rot
(keeps coverage honest without a GIF in CI).

---

## Out of scope

- Making `base_url` env-configurable (the clients hardcode it as a `ClassVar`; W-G does not need
  it — `responses` intercepts in-process). Defer unless a later need appears.
- Any new Yandex resource (that is `/new-endpoint`'s job).
- Token-leak scanning (separate work, per ARCH-5 scope note).

## Testing strategy

TDD per task. `responses` stubs all HTTP (no live network). MCP wiring tests marked
`@pytest.mark.integration`. Snapshots regenerated only on purpose. Final gate:
`uv run pytest` (100% cov) + `ruff format --check` + `ruff check` + `lint-imports` + `ty check`.

## Release

Public-surface **removal** (CLI `full`, MCP `issues_full`) is breaking; the `status_get` tool is an
addition. On a pre-1.0 line (0.8.1) semantic-release maps a breaking change to a **minor** bump
→ **0.9.0**. Squash-merge title decided at merge (likely `feat!:` with a `BREAKING CHANGE:` footer
naming the removed `full` command/tool). After release: `uv lock` + `build:` sync commit (PSR
bumps pyproject but not the lock).

## Decisions locked (from review)

| Point | Decision |
|-------|----------|
| 3 RawMapping | Delete `full` + `RawMapping` + `get_raw` entirely |
| 4 status | `yandex/status/` package + read-only `status_get` MCP tool |
| 4 mcp_cli | `ycli/mcp/` package (server in `__init__.py`, cli in `cli.py`, `__main__.py`) |
| 6 pagination | PEP 695 generics + `Envelope` protocol; fold `collect_single_page` into a class |
| 7 status `me` | Bare native `me` object (drop `ServiceProbe` + identity lambdas; keep valid/detail) |
| MCP naming | `status_get` in new `status` namespace |
| demo | Variant B (fixtures + real CLI render via `responses`; mcp list from live `methods`) |
