# Architecture

`ycli` exposes one SDK four ways (CLI, MCP server, Python SDK, Claude Code plugin).
Its strength is a regular, symmetric layout — and that regularity is enforced, not hoped for.
These invariants are checked by `tests/test_architecture.py`, import-linter (`pyproject.toml`),
and `tests/test_snapshots.py`. A failing build names the violated invariant.

## Layout

```
src/ycli/
├── cli/ · mcp/ · log.py · settings.py  # roots (cli/ = app · context · output)
└── yandex/
    ├── core/          # httpx2 core: endpoint · pagination · session · auth · profile · resource
    ├── base.py · transport.py · pagination.py  # the uplink stack, until every resource moved
    ├── mcp.py · registry.py · service.py       # MCP helpers, the service list
    └── <domain>/                            # tracker · wiki · forms
        ├── base.py · dependencies.py · typedefs.py · client.py · cli.py · mcp.py
        └── <resource>/                      # issues · pages · surveys · …
            ├── endpoints.py  # core resources: each operation declared once (sans-IO)
            ├── client.py   # the SDK — sends endpoints (core) or uplink calls; the ONLY HTTP
            ├── cli.py      # Typer — commands return results; output.render prints them
            ├── mcp.py      # FastMCP tools (reads + writes, honest hints)
            ├── models.py   # pydantic (inherit APIModel from ycli.yandex.models)
            └── __init__.py
```

Notable shared pieces:
- `src/ycli/settings.py` — `AppConfig` + `Credentials` pydantic-settings models (app-wide config)
- `src/ycli/yandex/models.py` — `APIModel` base (lenient parse config, no serialization logic)
- `src/ycli/cli/context.py` — `AppContext` (typed composition root for the CLI); `cli/inject.py`
  fills a command's keyword-only client/config parameters from it
- `src/ycli/yandex/core/` — the httpx2 core: `Endpoint[T]` (an operation declared once with its
  effect), one `Pagination` class per Yandex paging kind, `SyncSession` / `AsyncSession` (typed
  errors, retries, logging, page walking), every auth kind as an `httpx2.Auth`, and
  `ServiceProfile` (base URL + organization header). Tracker `issues` runs on it; the other
  resources move in E2
- `src/ycli/yandex/pagination.py` — the uplink resources' pagination strategies (until E2)
- `src/ycli/yandex/mcp.py` — shared MCP annotation helpers (`RO`) plus the per-request
  client/config providers (`client_provider`, `app_config`): credentials are resolved on every
  tool call, so nothing is cached per process
- `src/ycli/cli/lazy.py` — the root group lists every sub-app from its declaration and imports it
  on first use, so `ycli --version` or one service's command never imports the others
- `src/ycli/yandex/registry.py` — `SERVICES`, the one list of services; the CLI root, the MCP
  server and `auth status` iterate it (each domain declares its `SERVICE` in `__init__.py`)
- `src/ycli/yandex/<domain>/typedefs.py` — deduplicated CLI argument/option type aliases;
  `src/ycli/cli/fields.py` — the shared `--field key=value` JSON coercion

## Invariants (ARCH-1..11)

- **ARCH-1 — Four-surface symmetry.** Every `yandex/<domain>/<resource>/` directory contains
  `__init__.py`, `client.py`, `cli.py`, `mcp.py`, `models.py`. Use `/new-endpoint` to scaffold.
  Beyond file existence, **operation-level parity** holds: every public client operation is
  wrapped on **both** the CLI and the MCP surface. Coverage is read structurally — which client
  method each surface's `cli.py` / `mcp.py` actually calls (`….<resource>.<op>(…)`) — so it
  holds even where the command or tool is *named* differently from the op
  (`checklists.create` → CLI `add`; `pages.get_by_id` → MCP `by_id_get`). The intentional
  asymmetries — CLI-only binary download/upload commands (raw `bytes` can't round-trip an MCP
  result), a CLI-only export-poll helper, and the SDK-internal `answers.list` primitive that
  `list_all` supersedes on both surfaces — are frozen in `ARCH1_SURFACE_ASYMMETRIES`
  (`tests/test_architecture.py`); a new unwrapped operation fails the build until it is wrapped
  on both surfaces or added there with a reason.
  *Carve-out:* `yandex/status/` and the `ycli/mcp/` server package are cross-cutting surfaces,
  not `<domain>/<resource>` dirs — the four-surface rule and the `_resource_dirs()` check
  (which scans only `tracker/wiki/forms`) do not apply to them.
- **ARCH-2 — HTTP confinement.** `cli.py`, `mcp.py`, and `models.py` never import `requests`,
  `uplink` or `httpx2`. All HTTP lives in `client.py` / `base.py` / `transport.py` and the
  `ycli.yandex.core` package, which itself imports no service and no surface (import-linter).
- **ARCH-3 — MCP mirrors the SDK with honest annotations.** `fastmcp` is imported only in
  modules named `mcp.py` and in the `ycli.mcp` server package (`src/ycli/mcp/server.py`; its
  `__init__.py` stays fastmcp-free so the base install loads the CLI sub-app without the
  extra). MCP tools cover reads **and writes**; honesty is enforced fail-closed: every tool's
  verb (its longest known `_`-suffix) must classify into the READ / WRITE / WRITE_IDEMPOTENT /
  DESTRUCTIVE maps in `tests/test_architecture.py` — an unknown verb fails the build and is
  added deliberately. Hints must match the class exactly: reads carry `readOnlyHint=True`
  (`RO`); writes carry `readOnlyHint=False` plus explicit `destructiveHint`/`idempotentHint`
  (the `WRITE` / `WRITE_IDEMPOTENT` / `DESTRUCTIVE` sets in `ycli.yandex.mcp`) — explicit
  because the MCP-spec default for an unannotated tool is `destructiveHint=true`. Every write
  tool carries the `write` tag; `ycli mcp start --read-only` hides the tag wholesale for
  cautious deployments. A read-classified tool never calls a client write method — directly
  or laundered one hop through a module-level helper in the same module (AST-checked).
  A write tool's `body` parameter is always the resource's typed pydantic request model, never
  bare `dict`/`dict[...]` (docs/conventions/resources.md §4) — fail-closed and AST-checked
  (`test_arch3_mcp_write_tool_bodies_are_typed`), with exactly one documented exception
  (`ARCH3_BODY_DICT_ALLOWLIST` in `tests/test_architecture.py`: `entities_set_permissions`,
  whose live wire shape the existing models don't represent).
- **ARCH-4 — One output path.** A CLI command returns its result and never prints: the root
  `result_callback` hands it to `output.render`, the only stdout writer. A pydantic model renders
  through the `--format` strategy; a `str` or `int` prints verbatim (raw page markdown, a count);
  `BinaryResult` writes bytes to a file or stdout; `ExitWith` renders, then exits non-zero.
  `model_dump_json`, `yaml.safe_dump`, and `json.dumps` appear only in `src/ycli/cli/output.py`
  (and `json.dumps` in `src/ycli/log.py`, which formats diagnostic log records for stderr, not
  command output). Models stay plain data. *Check:* `test_arch4_commands_return_and_never_print`
  (AST: no `print(`, no `typer.echo`/`secho` without `err=True`, no `sys.stdout` in any `cli.py`)
  plus the serialization-call grep.
- **ARCH-5 — Single sources of truth.** No hardcoded version literal, `YANDEX_ID_*` token, or
  org-header string in `src/` outside `transport.py` (headers) and `__init__.py` (version, read
  from `importlib.metadata`).
- **ARCH-6 — Public-surface stability.** The CLI command tree and MCP tool list change only by
  regenerating the snapshots in `tests/snapshots/` on purpose.
- **ARCH-7 — Composition-root dependency injection.** Clients receive their dependencies as
  constructor arguments and never read the environment. Credentials enter only as the explicit
  `oauth_token` / `organization_id` parameters; a client never constructs a settings object or
  reads env. There is no `from_env` on any client. *Check:* grep — no `os.environ`, no
  `from_env`, no `Credentials(` / `AppConfig(` inside `yandex/**/client.py` or `base.py`.
- **ARCH-8 — Single configuration source.** No direct `os.environ` access and no `BaseSettings`
  subclass definition outside `src/ycli/settings.py`; other modules obtain configuration
  by instantiating the settings models (`Credentials()` / `AppConfig()`). *Check:* grep —
  `os.environ` and `class …(BaseSettings)` appear only in `settings.py`.
- **ARCH-9 — Typed boundary errors.** Non-2xx responses raise a typed `YandexError` subclass
  (one mapping, `errors.error_for_status`) from the uplink transport hook or the core session;
  no surface parses an error body into a model. *Check:* the existing
  status→exception mapping test, plus no `raise_for_status` / status-branching outside
  `transport.py`.
- **ARCH-10 — No shadowing of configurable values.** A configurable value is never overridden by
  a hardcoded literal that wins over the configured one (the `@uplink.timeout(30)` bug). *Check:*
  grep — no `@uplink.timeout` anywhere. Domain clients take an `HTTPConfig` (default:
  `HTTPConfig()`), so the SDK has no second copy of the timeout and retry defaults.
- **ARCH-11 — Doc-drift guard.** User-facing docs (`README.md`, `CLAUDE.md`, `AGENTS.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, `docs/conventions/**/*.md`,
  `plugins/**/*.md`) must not show call-site usage of idioms purged by ARCH-7..10. Concretely,
  the call patterns `.from_env(` and `session_from_env(` must not appear in any of those files.
  Historical / rule-defining files are intentionally excluded: `PROMPT.md` (transcript),
  `CHANGELOG.md` (release history), and `ARCHITECTURE.md` itself (which defines the rules).
  *Check:* `test_arch11_no_purged_idioms_in_live_docs` in `tests/test_architecture.py`.

## Scope & limits of enforcement

The checks are guardrails, not a proof. Known boundaries (the `/arch-review` rubric and human
review cover the rest):

- **ARCH-2/ARCH-3 catch _direct_ imports** (`allow_indirect_imports=true`, since `cli.py`/`mcp.py`
  legitimately reach HTTP transitively through `client.py`). An HTTP call hidden behind a new
  helper module that `cli.py` imports is not caught by import-linter.
- **ARCH-1 operation parity reads _direct_ surface→client calls.** A CLI/MCP wrapper that reaches
  the client through a local alias (`res = app_ctx.tracker.issues; res.get(…)`) instead of the
  canonical `….<resource>.<op>(…)` chain is not seen as coverage, so it would surface as a
  (false) asymmetry — flagged deliberately, so the non-standard wrapping has to be made explicit
  (wired straight, or allowlisted). The silent false-*negative* twin: an unrelated same-named
  `X.<resource>.<op>(…)` chain elsewhere in the surface file could satisfy the structural match
  and mask a genuinely-missing wrapper. The same receiver-chain heuristic (a call is a client
  op only when its receiver names a known resource) also backs the ARCH-3 read-tool backstop, so
  a client write verb (`update`/`add`/`clear`/…) is not confused with the like-named container
  method on a bare local.
- **ARCH-5 is single-source-of-truth, not secret scanning.** It catches hardcoded `__version__`,
  `YANDEX_ID_*` assignments, and org-header strings — not an arbitrary raw token literal (that is
  the job of the token-leak guard, a separate piece of work).
- **ARCH-10 enforces the timeout/retries case, not `max_items`.** The `@uplink.timeout` grep plus
  the SDK-defaults test cover the historical shadowing bug. A hardcoded pagination cap is NOT
  grep-enforced — a literal `500` collides with the HTTP `500` status code in `transport.py`, so a
  reliable check isn't worth the false positives; call sites read `AppConfig().http.max_items`, and the
  single-config-source rule (ARCH-8) keeps the default in `settings.py`.
- **ARCH-6 locks names, not signatures.** A tool/command keeping its name while changing its
  parameters, description, or return type does not trip the snapshot.

## Resource conventions (models, naming, MCP imports)

The conventions that ARCH-1..11 do not capture — `APIModel` inheritance, `XList`/`XResponse`
naming and the `dependencies` import path — are documented in
[`docs/conventions/resources.md`](docs/conventions/resources.md).

## Code generation

Resources are hand-written, starting from the `/new-endpoint` scaffold
(`scripts/new_endpoint.py`). Generating them from a spec is being built in a separate repo,
[`refract`](https://github.com/bim-ba/refract): one YAML spec per resource compiles into the
same committed file layout, and ycli's hand-written code is the golden output it must
reproduce. ycli does not use refract yet. Rejected: generating clients or tools at runtime
(metaprogramming), and external SDK generators such as Fern, which cover only the SDK and
impose their own models. The HTTP stack moves to the httpx2 core independently of refract
(#85): its `Endpoint[T]` has the same shape as refract's `Request`, so generated resources can
target it; the uplink stack is removed once the last domain has moved (E2).

## Changing an invariant

These are deliberate, not incidental. To change one: edit this file **and** its enforcing check
(in `tests/test_architecture.py`, `pyproject.toml`, or the snapshots) **in the same PR**, and say
so in the PR body. A reviewer (human or `/arch-review`) should reject a surface/structure change
that isn't reflected here.
