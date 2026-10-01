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

## Invariants (ARCH-1..8)

Each rule states a principle; the mechanics live in its check, and every exception is an
allowlist entry in code with its reason, never prose here. Tests are in
`tests/test_architecture.py` unless named otherwise.

### ARCH-1 — Surface parity
- **Rule:** every public SDK operation is wrapped on both the CLI and the MCP surface.
- **Why:** one operation behaves the same however a person or an agent reaches it.
- **Check:** `test_arch1_four_surface_symmetry` (each `<domain>/<resource>/` has `client.py`,
  `cli.py`, `mcp.py`, `models.py`, `__init__.py`; `/new-endpoint` scaffolds them) and
  `test_arch1_operation_level_parity`, which reads which client method each surface actually
  calls, so a command may be named differently from its operation.
- **Exceptions:** `ARCH1_SURFACE_ASYMMETRIES` — binary download/upload is CLI-only (bytes do not
  round-trip an MCP result), plus a few SDK-internal primitives. `status/` and the `ycli.mcp`
  server package are cross-cutting surfaces, not resources.

### ARCH-2 — Layers
- **Rule:** dependencies point one way — the core knows no service, services know no surface's
  framework, surfaces never import each other.
- **Why:** each layer has one job (single responsibility) and can change without the others.
- **Check:** import-linter contracts in `pyproject.toml` (`uv run lint-imports`): the httpx2
  core imports no service, surface, `typer` or `fastmcp`; MCP modules never import `ycli.cli`
  or `typer`, even indirectly; `cli.py`/`mcp.py`/`models.py` import no HTTP library
  (`requests`, `uplink`, `httpx2`) directly — HTTP lives in `client.py`, the uplink
  `transport.py`/`base.py` and `ycli.yandex.core`; `fastmcp` is not imported directly by the
  CLI, clients, models or the `ycli.mcp` package `__init__` (the base install loads `ycli mcp`
  without the extra).
- **Exceptions:** the MCP server and `ycli mcp methods` import `fastmcp` (`ignore_imports`).
  Imports under `if TYPE_CHECKING:` are ignored (they never run).

### ARCH-3 — Honest effects
- **Rule:** what an operation does to the server (read, write, idempotent write, destructive) is
  declared once, and MCP annotations, the `write` tag and `--read-only` agree with it.
- **Why:** agents and their hosts decide what to auto-approve from these hints; the MCP default
  for an unannotated tool is "destructive".
- **Check:** for resources on the httpx2 core,
  `test_arch3_core_tools_are_annotated_by_their_endpoint_effect` runs every tool and compares
  its hints with the effect of the first `Endpoint` it sends (`ARCH3_EFFECT_CASES`, fail-closed
  both ways), and `test_arch3_effect_overrides_are_listed` keeps every `effect=` that differs
  from the method in `ARCH3_EFFECT_OVERRIDES`. An AST check stops any tool that is read-only by
  name or by its `RO` hints from calling a client write method. For resources still on uplink,
  the verb maps classify each tool by name; they go away with the last uplink resource (E2), and
  `test_arch3_verb_maps_are_still_needed` fails at that point to say so.
  `test_arch3_write_tools_carry_write_tag` keeps `--read-only` complete.
- **Exceptions:** `ARCH3_EFFECT_OVERRIDES` (a read over `POST`, an idempotent `POST`).

### ARCH-4 — One output path
- **Rule:** a CLI command returns its result; only `output.render` writes to stdout.
- **Why:** one place decides formats, so `--format` and piping behave the same everywhere.
- **Check:** `test_arch4_commands_return_and_never_print` (AST: no `print`, `rich.print`, stdout
  `Console`, `typer.echo` without `err=True`, `sys.stdout` or `os.write` in any `cli.py`) and
  `test_arch4_serialization_confined_to_output`.
- **Exceptions:** `log.py` formats stderr log records with `json.dumps`. Bytes and raw text
  are result types (`BinaryResult`, `str`), not exceptions.

### ARCH-5 — Single sources of truth
- **Rule:** every value has one home: the version in package metadata, environment access
  (`os.environ`, `os.getenv`, `from_env`) and settings models in `settings.py`, the org header
  name in `core/profile.py`, API hosts in each service's profile, timeout/retry/limit defaults
  in the settings models (no `timeout=30`-style literal elsewhere).
- **Why:** a second copy drifts, and a hardcoded literal silently beats configuration (the old
  `@uplink.timeout(30)` bug).
- **Check:** `test_arch5_single_sources_of_truth` (+ `test_arch5_guard_bites`).
- **Exceptions:** `ARCH5_HOST_HOMES` — the IAM token endpoint and the OAuth login flow.

### ARCH-6 — The public surface is versioned
- **Rule:** the CLI tree, MCP tool names and both surfaces' parameters (name, type, default,
  required) change only on purpose.
- **Why:** scripts and agents depend on them; a silent rename or new required parameter breaks
  them.
- **Check:** `tests/test_snapshots.py` against `tests/snapshots/{cli_tree,mcp_tools,cli_signatures,mcp_signatures}.txt`;
  accept a change with `uv run python -m tests.snapshots --update`.
- **Exceptions:** none. Fields nested inside an MCP `body` model are not snapshotted.

### ARCH-7 — Dependency injection
- **Rule:** only composition roots build settings from the environment; everything else
  receives configuration and clients as arguments.
- **Why:** code that reads the environment itself cannot be reused or tested in isolation.
- **Check:** `test_arch7_settings_are_built_only_at_composition_roots` (AST: calls, attribute
  calls, import aliases and bare references such as `default_factory=AppConfig`).
- **Exceptions:** `ARCH7_ROOTS` — the CLI root and its dependency container, the MCP providers
  and entry point, and `auth status`/`login`, which read and write credentials by design.

### ARCH-8 — Typed boundaries
- **Rule:** data crosses a boundary as a parsed model: MCP write bodies are typed request
  models, and a non-2xx answer becomes a typed `YandexError` in one place
  (`errors.error_for_status`).
- **Why:** parse, don't validate — a malformed value fails at the edge with a clear error.
- **Check:** `test_arch8_mcp_write_tool_bodies_are_typed` and
  `test_arch8_errors_are_mapped_in_one_place` (each with a bite test): `raise_for_status`
  nowhere, `error_for_status` only in `ARCH8_ERROR_MAPPERS`.
- **Exceptions:** `ARCH8_BODY_DICT_ALLOWLIST` (`entities_set_permissions`, whose wire shape no
  model represents yet); `ARCH8_ERROR_MAPPERS` (the two transports and the IAM token exchange).

## Scope & limits of enforcement

The checks are guardrails, not a proof; the `/arch-review` rubric and human review cover the
rest. Known blind spots:

- **ARCH-1 parity reads direct surface→client calls.** A wrapper that reaches the client through
  a local alias is reported as a (false) gap; an unrelated same-named `X.<resource>.<op>(…)`
  call could mask a real one. It is an AST scan, not yet the per-endpoint flags planned for
  when every resource is declared as endpoints (E2).
- **ARCH-2 catches direct imports only** for the HTTP-library and `fastmcp` contracts
  (`allow_indirect_imports = true`, since surfaces reach HTTP through `client.py`): an HTTP call
  hidden in a helper module that `cli.py` imports is not caught.
- **ARCH-3's effect check sees the first request** a core tool sends; a tool that reads and
  then writes is caught by the read-tool AST check only if it is read-only by name or hints.
- **ARCH-3's uplink half guesses from names** until those resources move to the core.
- **ARCH-5 is not secret scanning** (gitleaks is). Its literal-default check reads keyword
  arguments (`timeout=30`), not a bare `500` elsewhere, which is indistinguishable from the
  HTTP status.
- **ARCH-7 reads names**: a settings model reached through a module alias it cannot resolve
  (`import ycli.settings as s; s.AppConfig()` is caught, `getattr(s, "AppConfig")()` is not).

## Resource conventions (models, naming, MCP imports)

The conventions that ARCH-1..8 do not capture — `APIModel` inheritance, `XList`/`XResponse`
naming and the `dependencies` import path — are documented in
[`docs/conventions/resources.md`](docs/conventions/resources.md).
What each resource is tested with, and how, is in
[`docs/conventions/testing.md`](docs/conventions/testing.md).

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
