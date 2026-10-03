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
    ├── base.py        # DomainClient: one core session per service, its resource clients
    ├── mcp.py · registry.py · service.py       # MCP helpers, the service list
    └── <domain>/                            # tracker · wiki · forms
        ├── dependencies.py · typedefs.py · client.py · cli.py · mcp.py
        └── <resource>/                      # issues · pages · surveys · …
            ├── endpoints.py  # each operation declared once (sans-IO)
            ├── client.py   # the SDK — a Resource that sends the endpoints; the ONLY HTTP
            ├── cli.py      # Typer — commands return results; output.render prints them
            ├── mcp.py      # FastMCP tools (reads + writes, honest hints)
            ├── models.py   # pydantic (inherit APIModel from ycli.yandex.models)
            └── __init__.py
```

Notable shared pieces:
- `src/ycli/settings.py` — `AppConfig` + `Credentials` pydantic-settings models (app-wide config)
- `src/ycli/yandex/models.py` — `APIModel` base (lenient parse config; dumps keep the API's field names)
- `src/ycli/cli/context.py` — `AppContext` (typed composition root for the CLI); `cli/inject.py`
  fills a command's keyword-only client/config parameters from it
- `src/ycli/yandex/core/` — the httpx2 core: `Endpoint[T]` (an operation declared once with its
  effect), one `Pagination` class per Yandex paging kind, `SyncSession` / `AsyncSession` (typed
  errors, retries, logging, page walking), every auth kind as an `httpx2.Auth`, and
  `ServiceProfile` (base URL + organization header). Every resource runs on it. Its auth and
  pagination kinds are a public part of the SDK, kept for services to come: one that no
  current service uses is not dead code
- `src/ycli/yandex/mcp.py` — shared MCP annotation helpers (`RO`) plus the per-request
  client/config providers (`client_provider`, `app_config`): credentials are resolved on every
  tool call, so nothing is cached per process
- `src/ycli/mcp/` — `server.build_server(Selection)` mounts only the selected services (so
  `--toolsets wiki` never imports Tracker); `selection.py` / `profiles.py` hold the typed flags
  and the curated `core` toolset, `listing.py` the transforms that slim `tools/list` and reject
  unknown tool names
- `src/ycli/cli/lazy.py` — the root group lists every sub-app from its declaration and imports it
  on first use, so `ycli --version` or one service's command never imports the others
- `src/ycli/yandex/registry.py` — `SERVICES`, the one list of services; the CLI root, the MCP
  server and `auth status` iterate it (each domain declares its `SERVICE` in `__init__.py`, and
  its client a `probe()` — the one cheap read `auth status` calls)
- `src/ycli/yandex/<domain>/typedefs.py` — deduplicated CLI argument/option type aliases;
  `src/ycli/cli/fields.py` — the shared `key=value` field parser (`--field`, and `ycli api`'s `-f`/`-F`)
- `src/ycli/cli/api.py` — `ycli api`, the raw passthrough: it builds an `Endpoint` and sends it with
  `DomainClient.send` / `iterate`, so retries, errors, `--dry-run` and the delete guard all apply. A
  CLI-only root command, not a resource, so ARCH-1 (per-resource parity) has no entry for it.
  `ycli doctor` (`yandex/status/doctor.py`) is one too: it runs the probes of `auth status`
  in order and says what to fix; an agent has `status_get`

## Invariants (ARCH-1..8)

Each rule states a principle; the mechanics live in its check, and every exception is an
allowlist entry in code with its reason, never prose here. Tests are in
`tests/test_architecture.py` unless named otherwise.

### ARCH-1 — Surface parity
- **Rule:** every public SDK operation is wrapped on both the CLI and the MCP surface, under one
  name: the CLI path (service, groups, leaf; spaces and hyphens as `_`) is the MCP tool name,
  the SDK method is that name without the service and resource (`tracker_boards_update` is
  `tracker.boards.update`), and one verb per action (`update`, never `edit` or `modify`). A renamed CLI command
  stops answering to its old name in the same release, and the changelog lists the old and the
  new name (the rule for models is in [`docs/conventions/resources.md`](docs/conventions/resources.md)).
- **Why:** one operation behaves the same however a person or an agent reaches it, and a name
  learned on one surface works on the other.
- **Check:** `test_arch1_four_surface_symmetry` (each `<domain>/<resource>/` has `endpoints.py`,
  `client.py`, `cli.py`, `mcp.py`, `models.py`, `__init__.py`; `/new-endpoint` scaffolds them;
  every directory of a service is a resource except `<domain>/mcp/`, the service's MCP server,
  a name `/new-endpoint` refuses: `test_arch1_a_reserved_directory_is_not_a_resource`) and
  `test_arch1_operation_level_parity`, which reads which client method each surface actually
  calls, so a command may be named differently from its operation.
  `test_arch1_every_resource_is_served` reads the running surfaces instead of the source: each
  resource directory is wired into its domain client, is a group of the built CLI tree and
  serves MCP tools from the mounted server, and nothing is served without a directory.
  `test_arch1_cli_path_equals_mcp_name` pairs each MCP tool with the CLI command that calls the
  same client operations and fails when their names differ or either uses a synonym verb.
  `test_arch1_sdk_method_equals_tool_name` holds the SDK method to the name of a tool that
  calls it (of the CLI command when no tool does; an operation reached only as a step of
  another has no name to match), and the endpoint builders and tool functions to the verbs.
  `test_arch1_tool_function_is_named_like_its_tool` holds the Python function behind a tool to
  the tool's name without the resource (`grids_rows_add` is `def rows_add`; a builtin's name
  takes a trailing underscore, `list_`).
- **Exceptions:** `ARCH1_NAME_EXCEPTIONS` — a tool with no CLI command of its own name because
  one command serves several tools; `ARCH1_SURFACE_ASYMMETRIES` — a binary download is
  CLI-only (bytes do not round-trip an MCP result), and so is an upload that reads a file
  from disk (the other uploads are MCP tools that take base64), plus a few SDK-internal primitives; a
  resource whose every operation is listed there serves no MCP tool. `status/` and the `ycli.mcp` server package are
  cross-cutting surfaces, not resources; `ARCH1_NON_RESOURCE_CLI_GROUPS` lists the CLI group every
  service mounts that is no resource (`<service> auth`, built once from the registry).

### ARCH-2 — Layers
- **Rule:** dependencies point one way — the core knows no service, services know no surface's
  framework, surfaces never import each other.
- **Why:** each layer has one job (single responsibility) and can change without the others.
- **Check:** import-linter contracts in `pyproject.toml` (`uv run lint-imports`): the httpx2
  core imports no service, surface, `typer` or `fastmcp`; MCP modules never import `ycli.cli`
  or `typer`, even indirectly; `cli.py`/`mcp.py`/`models.py` import no HTTP library
  (`httpx2`) directly — HTTP lives in `client.py` and `ycli.yandex.core`; `fastmcp` is not imported directly by the
  CLI, clients, models or the `ycli.mcp` package `__init__` (the base install loads `ycli mcp`
  without the extra).
- **Exceptions:** the MCP server (`ycli.mcp.server`) and its listing transforms
  (`ycli.mcp.listing`) import `fastmcp` (`ignore_imports`); `ycli mcp start` / `methods` import
  the server lazily, behind the extra.
  Imports under `if TYPE_CHECKING:` are ignored (they never run).

### ARCH-3 — Honest effects
- **Rule:** what an operation does to the server (read, write, idempotent write, destructive) is
  declared once, and MCP annotations, the `write` tag and `--read-only` agree with it.
- **Why:** agents and their hosts decide what to auto-approve from these hints; the MCP default
  for an unannotated tool is "destructive".
- **Check:** the contract test (`tests/test_contract.py`, one case per way of reaching an
  operation, fail-closed both ways) runs every tool and compares its hints with the strongest
  effect of the endpoints it sends; `test_arch3_effect_overrides_are_listed` keeps every
  `effect=` that differs from the method in `ARCH3_EFFECT_OVERRIDES`;
  `test_arch3_write_tools_carry_write_tag` keeps `--read-only` complete. `status_get`, the one
  tool outside a resource, is checked on its own (`tests/yandex/status/test_mcp.py`).
  A prompt and a resource follow their tools (`tests/test_mcp_prompts_resources.py`): a
  prompt lists the tools its text names, all of them exist, and one write among them means
  the `write` tag; a resource template names the read tool it repeats and returns what that
  tool returns; the server offers neither when one of those tools is not served, so `--read-only`
  and every other selection flag cover them without a rule of their own.
- **Exceptions:** `ARCH3_EFFECT_OVERRIDES` (a read over `POST`, an idempotent `POST`).

### ARCH-4 — One output path
- **Rule:** a CLI command returns its result; only `output.render` writes to stdout.
- **Why:** one place decides formats, so `--format` and piping behave the same everywhere.
- **Check:** `test_arch4_commands_return_and_never_print` (AST over every module, import aliases
  resolved: no `print` in any spelling — `builtins.print`, `rich.print`, `pprint` — no stdout
  `Console`, `typer.echo` without `err=True`, `sys.stdout`/`sys.__stdout__` or `os.write`) and
  `test_arch4_serialization_confined_to_output` (AST: `json.dumps`, `yaml.safe_dump`,
  `pydantic_core.to_json`, `.model_dump_json()` and their aliases), each with a bite test.
- **Exceptions:** `ARCH4_SERIALIZATION_HOMES` (`log.py` formats stderr log records with
  `json.dumps`) and `ARCH4_STDOUT_FUNCTIONS` (the eager `--version` callback, and
  `guard.attended`, which only asks whether stdout is a terminal). Bytes and raw text are result
  types (`BinaryResult`, `str`), not exceptions.
- **Field names:** CLI and MCP output both keep each API's own field names (Tracker
  `createdAt`, Wiki `created_at`), so a key reads the same in the vendor docs, in `--format json`
  and in a tool result; Python code reads snake_case attributes. `APIModel` sets
  `serialize_by_alias`, and `test_tool_output_uses_the_api_field_names` keeps the MCP side honest.

### ARCH-5 — Single sources of truth
- **Rule:** every value has one home: the version in package metadata, environment access
  (`os.environ`, `os.getenv`), settings models and the credential variable names
  in `settings.py`, the org header name in `core/profile.py`, API hosts in each service's
  profile, a logger name in the one module that spells it. A limit a user can run into
  (timeout, retries, item cap, page cap, the longest `Retry-After`) is a default in the settings
  models, with no `timeout=30`-style literal or `MAX_…` constant elsewhere; a fact of the API
  (a page size it accepts, a status code) is a named constant in the module that uses it.
- **Why:** a second copy drifts, and a hardcoded literal silently beats configuration.
- **Check:** `test_arch5_single_sources_of_truth` (+ `test_arch5_guard_bites`);
  `test_arch5_every_host_home_still_spells_a_host` keeps the allowlist free of stale entries, and
  `test_arch5_a_logger_name_is_spelled_in_one_module` (+ bite test) the logger names single.
- **Exceptions:** `ARCH5_HOST_HOMES` — the IAM token endpoint, the Yandex ID / API 360 hosts
  `auth status` reads, and PyPI. The version check of `ycli doctor` is the one request ycli sends
  to a host that is not Yandex's, and it carries no credentials.

### ARCH-6 — The public surface is versioned
- **Rule:** the CLI tree, MCP tool names and both surfaces' parameters (name, type, default,
  required), and the MCP prompts (with their arguments) and resource addresses, change only on
  purpose.
- **Why:** scripts and agents depend on them; a silent rename or new required parameter breaks
  them.
- **Check:** `tests/test_snapshots.py` against `tests/snapshots/{cli_signatures,mcp_signatures,mcp_prompts_and_resources}.txt`;
  accept a change with `uv run python -m tests.snapshots --update`.
- **Exceptions:** none. Fields nested inside an MCP `body` model are not snapshotted.

### ARCH-7 — Dependency injection
- **Rule:** only composition roots build settings from the environment; everything else
  receives configuration and clients as arguments.
- **Why:** code that reads the environment itself cannot be reused or tested in isolation.
- **Check:** `test_arch7_settings_are_built_only_at_composition_roots` (AST: calls, attribute
  calls, import aliases, bare references such as `default_factory=AppConfig`, a constructor
  such as `Credentials.load()`, and the functions that read or name the active profile);
  `test_arch7_every_root_still_builds_settings` removes a root that stopped being one.
- **Exceptions:** `ARCH7_ROOTS` — the CLI root and its dependency container, the MCP providers
  and entry point, `mcp start`, which names the profile its providers read, and
  `auth status`/`login`/`profiles`, which read and write credentials by design.

### ARCH-8 — Typed boundaries
- **Rule:** data crosses a boundary as a parsed model: a request body is a typed request
  model from the MCP tool and the CLI command down to the endpoint, which dumps it once
  (`core.endpoint.dump_body`), and a non-2xx answer becomes a typed `YandexError` in one place
  (`errors.error_for_status`).
- **Why:** parse, don't validate — a malformed value fails at the edge with a clear error.
- **Check:** `test_arch8_mcp_write_tool_bodies_are_typed` (no `body: dict` in an MCP tool, a
  client method or an endpoint builder), `test_arch8_a_request_body_is_dumped_only_by_the_endpoint`
  (none of the three dumps a model) and
  `test_arch8_errors_are_mapped_in_one_place` (each with a bite test): `raise_for_status`
  nowhere; outside `ARCH8_ERROR_MAPPERS`, no `error_for_status`, no `status_code` read and no
  hand-built status-carrying `YandexError` (AST, import aliases resolved).
- **Exceptions:** `ARCH8_BODY_DICT_ALLOWLIST` (empty); `ARCH8_ERROR_MAPPERS` (the core sessions, the IAM token exchange and
  the OAuth login flow, whose device-flow polling states arrive as HTTP 400);
  `ARCH8_LOCAL_RAISES` (a request refused before it is sent, a 2xx whose body is empty); `ARCH8_STATUSLESS_ERRORS` (a
  timeout or a lost connection has no status to map).

## Scope & limits of enforcement

The checks are guardrails, not a proof; the `/arch-review` rubric and human review cover the
rest. Known blind spots:

- **ARCH-1 parity reads direct surface→client calls.** A wrapper that reaches the client through
  a local alias is reported as a (false) gap; an unrelated same-named `X.<resource>.<op>(…)`
  call could mask a real one. The served-surface check works per
  resource: it sees an unmounted resource, not one unregistered tool inside a mounted one.
- **ARCH-2 catches direct imports only** for the HTTP-library and `fastmcp` contracts
  (`allow_indirect_imports = true`, since surfaces reach HTTP through `client.py`): an HTTP call
  hidden in a helper module that `cli.py` imports is not caught.
- **ARCH-3's effect check sees the requests a contract case makes**: a branch no case takes is
  not checked.
- **ARCH-5 is not secret scanning** (gitleaks is). Its literal-default check reads keyword
  arguments, annotated defaults and `MAX_…` / `DEFAULT_…` module constants (`timeout=30`,
  `retries: int = 3`, `MAX_PAGES = 1000`), not a bare `500` elsewhere, which is indistinguishable
  from the HTTP status, and not a limit under another name (`attempts=30` of the polling loop).
- **ARCH-7 reads names**: a settings model reached through a module alias it cannot resolve
  (`import ycli.settings as s; s.AppConfig()` is caught, `getattr(s, "AppConfig")()` is not).
  ARCH-4 and ARCH-8 read names the same way: `getattr(builtins, "print")`, a write to file
  descriptor 1 through `open(1, "w")`, or a branch on `response.ok` / `response.is_error` are not
  caught.

## Resource conventions (models, naming, MCP imports)

The conventions that ARCH-1..8 do not capture — `APIModel` inheritance, `ItemList[X]`/`XResponse`
naming and the `dependencies` import path — are documented in
[`docs/conventions/resources.md`](docs/conventions/resources.md).
What each resource is tested with, and how, is in
[`docs/conventions/testing.md`](docs/conventions/testing.md).

## Code generation

Resources are hand-written, starting from the `/new-endpoint` scaffold
(`scripts/new_endpoint.py`), which generates a resource on the httpx2 core (`endpoints.py` plus
a `Resource` client). Generating them from a spec is being built in a separate repo,
[`refract`](https://github.com/bim-ba/refract): one YAML spec per resource compiles into the
same committed file layout, and ycli's hand-written code is the golden output it must
reproduce. ycli does not use refract yet. The opposite direction is in use: `scripts/gen_openapi.py` derives an OpenAPI
document per service from the code at build time, for the docs site. Rejected: generating clients or tools at runtime
(metaprogramming), and external SDK generators such as Fern, which cover only the SDK and
impose their own models. The core's `Endpoint[T]` has the same shape as refract's `Request`,
so generated resources can target it.

## Changing an invariant

These are deliberate, not incidental. To change one: edit this file **and** its enforcing check
(in `tests/test_architecture.py`, `pyproject.toml`, or the snapshots) **in the same PR**, and say
so in the PR body. A reviewer (human or `/arch-review`) should reject a surface/structure change
that isn't reflected here.
