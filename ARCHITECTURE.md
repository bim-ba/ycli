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
    ├── base.py · transport.py · pagination.py · mcp.py  # shared (mcp.py = MCP helpers)
    └── <domain>/                            # tracker · wiki · forms
        ├── base.py · dependencies.py · typedefs.py · utils.py · client.py · cli.py · mcp.py
        └── <resource>/                      # issues · pages · surveys · …
            ├── client.py   # uplink SDK — the ONLY place HTTP happens
            ├── cli.py      # Typer — output via Serializer.serialize
            ├── mcp.py      # FastMCP tools (reads + writes, honest hints)
            ├── models.py   # pydantic (inherit APIModel from ycli.yandex.models)
            └── __init__.py
```

Notable shared pieces:
- `src/ycli/settings.py` — `AppConfig` + `Credentials` pydantic-settings models (app-wide config)
- `src/ycli/yandex/models.py` — `APIModel` base (lenient parse config, no serialization logic)
- `src/ycli/cli/context.py` — `AppContext` (typed composition root for the CLI)
- `src/ycli/yandex/pagination.py` — `PaginationStrategy` ABC + concrete strategies
- `src/ycli/yandex/mcp.py` — shared MCP annotation helpers (`RO`) plus the `@cache`d client/config
  providers (`make_cached_client`, `app_config`) that share one client across a mounted domain's tools
- `src/ycli/yandex/<domain>/typedefs.py` — deduplicated CLI argument/option type aliases;
  `utils.py` — shared CLI helpers where a domain needs them (tracker: request-body builders,
  `--field` JSON coercion)

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
- **ARCH-2 — HTTP confinement.** `cli.py`, `mcp.py`, and `models.py` never import `requests` or
  `uplink`. All HTTP lives in `client.py` / `base.py` / `transport.py`.
- **ARCH-3 — MCP mirrors the SDK with honest annotations.** `fastmcp` is imported only in
  modules named `mcp.py` and in the `ycli.mcp` server package (`src/ycli/mcp/server.py`; its
  `__init__.py` stays fastmcp-free so the base install loads the CLI sub-app without the
  extra). MCP tools cover reads **and writes**; honesty is enforced fail-closed: every tool's
  verb (its longest known `_`-suffix) must classify into the READ / WRITE / WRITE_IDEMPOTENT /
  DESTRUCTIVE maps in `tests/test_architecture.py` — an unknown verb fails the build and is
  added deliberately (most recently ``set_operator``, the display-conditions collection
  PATCH, registered as WRITE_IDEMPOTENT). Hints must match the class exactly: reads carry `readOnlyHint=True`
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
- **ARCH-4 — Serialization confinement.** Model→output rendering happens only through
  `output.Serializer.serialize(...)`; `model_dump_json`, `yaml.safe_dump`, and `json.dumps`
  appear only in `src/ycli/cli/output.py`. Models stay plain data (no serialize method); the
  strategies live only in `output.py`. Every rendered value is a typed pydantic model — there
  is no raw-dict/`RawMapping` escape hatch.
  *Carve-outs:* (a) a bare `print(int)` for a scalar `count` result is fine — it is not model
  output and needs no Serializer wrapping; (b) a **binary download** command writes raw
  `bytes` to a file/stdout via `ycli.cli.binary.write_output` (attachments, exports, keyset
  files) — bytes are not a model, so they bypass the Serializer too; (c) the `wiki pages get`
  command prints a page's **raw YFM markdown** body (`….content`) with a bare `print(` — the
  body is already a string (not a model to render) and is pinned this way so a piped/demo
  render stays verbatim. These three files with an allowed bare print
  (`tracker/issues/cli.py`, `wiki/pages/cli.py`) are the closed allowlist; no other path
  touches the three serialization calls. *Check:* `model_dump_json` / `yaml.safe_dump` /
  `json.dumps` only in `output.py`; CLI command bodies render model output via
  `Serializer.serialize`, and no `cli.py` outside the carve-out allowlist uses a bare `print(`.
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
  from the transport hook; no surface parses an error body into a model. *Check:* the existing
  status→exception mapping test, plus no `raise_for_status` / status-branching outside
  `transport.py`.
- **ARCH-10 — No shadowing of configurable values.** A configurable value is never overridden by
  a hardcoded literal that wins over the configured one (the `@uplink.timeout(30)` bug). *Check:*
  grep — no `@uplink.timeout` anywhere. **Carve-out:** the public SDK constructor signature
  defaults (`timeout_seconds: int = 30`, `retries: int = 3`) are parameter defaults, not
  shadowing — they apply only when the caller passes nothing, and `AppContext` always passes the
  configured value. These two literals must stay equal to `AppConfig`'s defaults; a test asserts
  `inspect.signature(TrackerClient).parameters` defaults == `AppConfig` field defaults so the
  duplication can't drift.
- **ARCH-11 — Doc-drift guard.** User-facing docs (`README.md`, `CLAUDE.md`, `AGENTS.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, `docs/conventions/**/*.md`,
  `plugins/**/*.md`) must not show call-site usage of idioms purged by ARCH-7..10. Concretely,
  the call patterns `.from_env(` and `session_from_env(` must not appear in any of those files.
  Historical / rule-defining files are intentionally excluded: `docs/superpowers/**` (specs),
  `PROMPT.md` (transcript), `CHANGELOG.md` (release history), and `ARCHITECTURE.md` itself
  (which defines the rules). *Check:* `test_arch11_no_purged_idioms_in_live_docs` in
  `tests/test_architecture.py`.

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
  reliable check isn't worth the false positives; call sites read `AppConfig().max_items`, and the
  single-config-source rule (ARCH-8) keeps the default in `settings.py`.
- **ARCH-6 locks names, not signatures.** A tool/command keeping its name while changing its
  parameters, description, or return type does not trip the snapshot.

## Resource conventions (models, naming, MCP imports)

The conventions that ARCH-1..11 do not capture — `APIModel` inheritance, `XList`/`XResponse`
naming and the `dependencies` import path — are documented in
[`docs/conventions/resources.md`](docs/conventions/resources.md).

## Changing an invariant

These are deliberate, not incidental. To change one: edit this file **and** its enforcing check
(in `tests/test_architecture.py`, `pyproject.toml`, or the snapshots) **in the same PR**, and say
so in the PR body. A reviewer (human or `/arch-review`) should reject a surface/structure change
that isn't reflected here.
