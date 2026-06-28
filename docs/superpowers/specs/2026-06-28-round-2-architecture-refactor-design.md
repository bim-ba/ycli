# Round-2 Architecture Refactor — Design

> Status: approved design, ready for an implementation plan.
> Fifth track, after A (guardrails, v0.3.0), B (AI-infra, v0.4.0), C (UX, v0.5.0), and the
> internals-cleanup track (v0.6.0). Lands as `feat:` → **v0.7.0**.

## Goal

Make ycli's internals match the design principles the maintainer has repeatedly asked for:
clean **dependency injection** (clients take raw credential arguments, never read the
environment), **centralized serialization** (one `Serializer` service, models stay plain
pydantic), and **encapsulated pagination** — so the public surface (CLI, MCP, importable SDK)
is simpler and scales. No new endpoints; behavior changes are limited to the deliberate ones
below (pagination ergonomics, friendlier SDK construction). The architecture invariants are
updated to encode the new principles.

## Decisions already taken (do not relitigate)

- **Composition-root DI.** Clients receive their credentials/session via the constructor and
  never read `os.environ`. The environment is read once at a composition root (the CLI
  `AppContext`, the MCP `lifespan`). `FromEnvSession` and every `from_env` are deleted.
- **Public SDK clients take raw credential arguments, not settings objects.** The three
  composition-root clients (`TrackerClient`/`WikiClient`/`FormsClient`) — the public SDK entry
  points — accept primitives: `oauth_token: str` (required), `organization_id: str`
  (required), `timeout_seconds: int = 30`, `retries: int = 3`, and an optional bare
  `session: requests.Session | None = None` for transport injection (tests, custom adapters/
  proxies). A client must **not** know about the `Credentials` / `AppConfig` settings objects —
  those are a composition-root concern. **The sole credentials entry is `oauth_token` +
  `organization_id`.** Passing a *pre-authenticated* session (one that already carries the auth
  headers) is **rejected** — it hides where credentials enter and lowers transparency; the
  injected `session` is a bare transport, and the client always applies auth headers +
  timeout/retry adapters from the explicit arguments.
- **Typed `AppContext`** replaces the `cliformat.output_format(ctx)` helper: one typed object
  on `ctx.obj` holding `output_format` + a console + the lazily-built domain clients, with a
  `from_typer_context` classmethod for typed retrieval.
- **Centralized serialization via a `Serializer` service.** A `Serializer` class exposes one
  `@staticmethod serialize(model: BaseModel, strategy: SerializationStrategy, console: Console)`
  — the single dispatch point that replaces the old global `_STRATEGIES` map and the scattered
  top-level helpers. Models stay **plain pydantic** (no `.serialize()` method); a shared
  `ApiModel` base carries only lenient parse config. Format→strategy resolution is a
  `SerializationStrategy.from_format(output_format)` factory. Reframes ARCH-4 to "serialization
  confinement".
- **Bounded auto-pagination via a `PaginationStrategy` ABC.** Clients follow cursors
  internally and return `Users`-style `RootModel` collections (no cursors in the public API),
  capped by a `limit` (default `YCLI_MAX_ITEMS`). The envelope models become internal
  per-page parsers.
- **Keep `auto` output format.** Rejected the "always pretty" idea (breaks `| jq` / agent
  piping).
- **No module-singleton config.** `Credentials()` raises on missing env; constructed per
  invocation at the composition root.
- **Stay synchronous on `requests`.** Async / uplink replacement remain out of scope.
- **ARCH-3 (MCP read-only) stays** until the future read/write-MCP milestone; this track adds
  no write tools.

## Open sub-decisions (flagged for spec review)

1. **`YCLI_MAX_ITEMS` default = 500.** A conservative bound that protects the MCP/LLM context
   while covering most interactive use. Overridable per call (`--limit`) and via the env var.
2. **Bounded results carry no truncation metadata.** A collection capped at `limit` is a pure
   `RootModel` (honoring "no pagination metadata in the public surface"); receiving exactly
   `limit` items implies "there may be more". `--all` (CLI) / `limit=None` (SDK) fetches
   uncapped. MCP tool descriptions state the cap so the model knows to narrow its query.

## Global constraints (every task inherits these)

- **Full, self-documenting names** — no abbreviations. New env var is `YCLI_MAX_ITEMS`.
- **No hand-edited dependency lists** — `uv add` only (this track likely needs none new).
- **100% coverage stays green** (`--cov-fail-under=100`); every new branch ships with a test.
- **Conventional Commits**; the branch squash-merges as `feat:` → **v0.7.0**.
- **Snapshots are intentional** (ARCH-6): the CLI tree changes (per-command `--limit`/`--all`
  options replace `--cursor`) and the MCP tool list is stable; regenerate
  `tests/snapshots/` and treat the diff as reviewed.
- **Branch → PR → explicit approval before merge**; never write a CI-skip token /
  `skip-checks` trailer.
- **Post-release chore:** after v0.7.0 publishes, run `uv lock` + a `build:` commit.

## Architecture invariant changes (ARCHITECTURE.md + tests/test_architecture.py, same PR)

Keep ARCH-1 (four-surface symmetry), ARCH-2 (HTTP confinement), ARCH-3 (MCP read-only),
ARCH-5 (single source of truth), ARCH-6 (snapshots). Change/add:

- **ARCH-4 — Serialization confinement (replaces "Output discipline").** Model→output
  rendering happens only through `output.Serializer.serialize(...)`; `model_dump_json` and
  `yaml.safe_dump` appear only in `src/ycli/output.py`. Models stay plain data (no serialize
  method); the strategies live only in `output.py`. *Check:* `model_dump_json` / `yaml.safe_dump`
  only in `output.py`; CLI command bodies render via `Serializer.serialize`.
- **ARCH-7 — Composition-root dependency injection (new).** Clients receive their
  dependencies as constructor arguments and never read the environment. Credentials enter only
  as the explicit `oauth_token` / `organization_id` parameters; a client never constructs a
  settings object or reads env. There is no `from_env` on any client. *Check:* grep — no
  `os.environ`, no `from_env`, no `Credentials(` / `AppConfig(` inside `yandex/**/client.py`
  or `base.py`.
- **ARCH-8 — Single configuration source (new).** No direct `os.environ` access and no
  `BaseSettings` *subclass definition* outside `src/ycli/yandex/settings.py`; other modules
  obtain configuration by *instantiating* the settings models (`Credentials()` / `AppConfig()`).
  *Check:* grep — `os.environ` and `class …(BaseSettings)` appear only in `settings.py`.
- **ARCH-9 — Typed boundary errors (new).** Non-2xx responses raise a typed `YandexError`
  subclass from the transport hook; no surface parses an error body into a model. *Check:*
  the existing status→exception mapping test, plus no `raise_for_status` / status-branching
  outside `transport.py`.
- **ARCH-10 — No shadowing of configurable values (new).** A configurable value is never
  *overridden* by a hardcoded literal that wins over the configured one (the `@uplink.timeout(30)`
  bug). *Check:* grep — no `@uplink.timeout`; no `max_items`/page-size literal at a call site
  inside `cli.py`/`mcp.py`/leaf `client.py`. **Carve-out:** the public SDK constructor signature
  defaults (`timeout_seconds: int = 30`, `retries: int = 3`) are *parameter* defaults, not
  shadowing — they apply only when the caller passes nothing, and `AppContext`/`lifespan` always
  pass the configured value. These two literals must stay equal to `AppConfig`'s defaults; a test
  asserts `inspect.signature(TrackerClient).parameters` defaults == `AppConfig()` defaults so the
  duplication can't drift.

## Items

### 1. Configuration — add `YCLI_MAX_ITEMS`

`AppConfig` (in `settings.py`) gains `max_items: int = Field(default=500,
validation_alias="YCLI_MAX_ITEMS")`. This is the default pagination cap.

### 2. Dependency-injection overhaul

**`transport.py`:** inline the org header (`"X-Org-Id"`) at its one use site (drop the
`ORGANIZATION_HEADER` constant). `Transport.session` stays env-free and parameterized, and
gains an optional `base: requests.Session | None` so a caller-supplied bare session can be
configured rather than replaced:

```python
class Transport:
    @staticmethod
    def session(*, oauth_token, organization_id, timeout_seconds=30, retries=3,
                base: requests.Session | None = None) -> requests.Session:
        session = base or requests.Session()
        session.headers.update({"Authorization": f"OAuth {oauth_token}", "X-Org-Id": organization_id})
        # mount the timeout + retry adapters built from timeout_seconds / retries
        return session
```

(Header casing stays per-service — Tracker `X-Org-ID` vs Wiki/Forms `X-Org-Id`; the existing
per-domain transport handles that.)

**Leaf resource clients** (`yandex/**/<resource>/client.py`): unchanged constructor —
`__init__(*, session)`. They never read env (already true once `from_env` is gone).

**Composition-root clients** (`tracker/client.py`, `wiki/client.py`, `forms/client.py`) —
the public SDK entry points. They take **raw primitives**, never settings objects:

```python
class TrackerClient:
    def __init__(
        self,
        *,
        oauth_token: str,
        organization_id: str,
        timeout_seconds: int = 30,
        retries: int = 3,
        session: requests.Session | None = None,   # optional BARE transport injection
    ) -> None:
        transport = Transport.session(
            oauth_token=oauth_token,
            organization_id=organization_id,
            timeout_seconds=timeout_seconds,
            retries=retries,
            base=session,                            # bare session is configured, not trusted as-is
        )
        self.issues = IssuesClient(session=transport)
        ...  # fan the one configured session out to all sub-clients
```

`oauth_token` / `organization_id` are required (no defaults — a missing credential is a caller
error, surfaced at the composition root). The injected `session` is a *bare* `requests.Session`
(e.g. the `responses`-patched session in tests, or one with a custom proxy/adapter); the client
**always** applies the auth headers + timeout/retry adapters on top of it, so credentials never
enter through a pre-built session. No `from_env`. `FromEnvSession` is deleted; `BaseYandex`
loses it. The `Transport.session` build moves out of `base.py` into the composition-root
constructors. `settings.py` no longer needs the `FromEnvSession` mixin.

**CLI composition root — `AppContext`.** New `src/ycli/context.py`:

```python
@dataclass
class AppContext:
    output_format: OutputFormat
    _credentials: Credentials | None = None      # resolved lazily on first client access
    _config: AppConfig | None = None
    _console: Console | None = None
    _clients: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_typer_context(cls, ctx: typer.Context) -> "AppContext":
        """Return the AppContext stored on ctx.obj (built by the root callback)."""
        return ctx.obj

    @property
    def console(self) -> Console:
        if self._console is None:
            self._console = Console()
        return self._console

    @property
    def strategy(self) -> SerializationStrategy:
        return SerializationStrategy.from_format(self.output_format)

    def _client(self, domain, factory):
        if domain not in self._clients:
            # AppContext is THE composition root: it reads settings here and hands the client
            # raw primitives — the client never sees Credentials/AppConfig.
            self._credentials = self._credentials or Credentials()   # raises if unset
            self._config = self._config or AppConfig()
            self._clients[domain] = factory(
                oauth_token=self._credentials.oauth_token,
                organization_id=self._credentials.organization_id,
                timeout_seconds=self._config.timeout_seconds,
                retries=self._config.retries,
            )
        return self._clients[domain]

    @property
    def tracker(self) -> TrackerClient: return self._client("tracker", TrackerClient)
    @property
    def wiki(self) -> WikiClient: return self._client("wiki", WikiClient)
    @property
    def forms(self) -> FormsClient: return self._client("forms", FormsClient)
```

The root callback (`cli.py`) builds `AppContext(output_format=output_format)` onto `ctx.obj`
and configures logging; it does NOT resolve credentials (so `--help` and cred-free commands
work). Credentials resolve lazily on first `.tracker`/`.wiki`/`.forms` access — a missing
credential raises `ValidationError`, caught by `main()`. The three `_clideps.py` modules are
deleted (their lazy-DI job moves into `AppContext`); commands call
`AppContext.from_typer_context(ctx).tracker` etc. `parse_fields` (currently in
`tracker/_clideps.py`) moves to a small `tracker/_args.py` (or stays a tracker-local helper).

**MCP composition root — `lifespan`.** `src/ycli/mcp.py` gains a FastMCP `lifespan=` async
context manager that reads `Credentials()`/`AppConfig()` once at startup and builds the three
clients from their raw values (`oauth_token=…, organization_id=…, timeout_seconds=…, retries=…`),
yielding them; the three `_deps.py` provider functions read `ctx.lifespan_context[...]`
instead of calling `from_env()`. (Confirm the installed fastmcp version's `lifespan`/Context
API during planning; fastmcp 3.4.2 supports `lifespan=` and `ctx.lifespan_context`.)

**`auth.py`** keeps its own credential carve-out: it constructs `Credentials()` directly to
report "not configured", and builds the three clients from its raw values (not via
`AppContext`, since `auth status` must run credential-free up to the point of reporting).

### 3. Serialization — `Serializer` service + strategies

Serialization is a **service**, not a model capability. Two new pieces in `src/ycli/output.py`
(so `model_dump_json` stays confined), plus a shared model base outside it.

**`Serializer`** — one static dispatch method, replacing the old global `_STRATEGIES` map:

```python
class Serializer:
    @staticmethod
    def serialize(model: BaseModel, strategy: SerializationStrategy, console: Console) -> None:
        strategy.render(model, console)
```

**`SerializationStrategy`** — ABC + concretes (`JsonStrategy`/`YamlStrategy`/`PrettyStrategy`/
`AutoStrategy`), each implementing `render(model, console)`. The concretes absorb the top-level
helpers: `_prettify`/`_kv_table`/`_list_table`/`_cell`/`_key_link`/`_KEY_RE` become
methods/attributes of `PrettyStrategy`. Format→strategy resolution is a factory classmethod
(no module global): `SerializationStrategy.from_format(output_format) -> SerializationStrategy`.
The top-level `render()` and `cliformat.output_format` are removed; `cliformat.py` is deleted.

**Model base — `ApiModel`** (new `src/ycli/models.py`, pure pydantic, no serialization): the
four scattered `_Lenient` bases (tracker, forms, two inline copies in wiki) consolidate into
one `ApiModel(BaseModel)` carrying `model_config = ConfigDict(extra="ignore",
populate_by_name=True)`. Every `models.py` class inherits `ApiModel`. Pagination collections
(item 4) are `RootModel[...]` subclasses; `Serializer.serialize` accepts any `BaseModel`
(including `RootModel`), so collections need no extra base.

- Command bodies become:
  ```python
  app = AppContext.from_typer_context(ctx)
  Serializer.serialize(app.tracker.issues.get(key), app.strategy, app.console)
  ```
- The public Python SDK returns plain `ApiModel` instances; SDK callers use pydantic directly
  (`.model_dump()`), and never need `Serializer` (presentation is a CLI concern). MCP keeps
  returning JSON via `output.py` (the only place `model_dump_json` lives).

### 4. Pagination — `PaginationStrategy`

New `src/ycli/yandex/pagination.py`:

```python
class PaginationStrategy(ABC):
    """Drives one API's page-cursor mechanics. Accumulates items up to `limit`."""
    @abstractmethod
    def collect(self, fetch_page, limit: int | None) -> list: ...
```

Concrete strategies, one per mechanic actually present in the Yandex APIs (the exact
per-endpoint inventory is built during planning by reading `docs/references/yandex/`):

- `SinglePageStrategy` — one request, extract the list field (wiki attachments/comments
  `{results}`; small unpaginated Tracker lists like priorities/issuetypes).
- `CursorStrategy` — follow `next_cursor` (wiki pages descendants).
- `NextUrlStrategy` — follow `next.next_url` (forms answers).
- `LinksStrategy` — follow `links.next` (forms surveys).
- `LinkHeaderStrategy` — follow RFC-5988 `Link` headers if any Tracker endpoint uses them
  (issues search / changelog) — include only if the docs confirm it; otherwise those stay
  `SinglePageStrategy`.

Each list client method declares its strategy + how to extract items from a page, calls
`strategy.collect(fetch_page, limit)`, and returns a `RootModel` collection (`Users`-style;
`Serializer.serialize` renders it like any model). The per-page envelope models
(`DescendantsResponse`, `AnswersResponse`,
`SurveyList`, …) become **internal** parse types (used inside the client to read one page),
not public return types.

Bound: `limit` defaults to `AppConfig.max_items` (`YCLI_MAX_ITEMS`). CLI list commands expose
`--limit N` (override the cap) and `--all` (uncapped, `limit=None`), replacing `--cursor`. MCP
list tools use the default cap (no cursor parameter); their descriptions state the cap.

### 5. Cleanups (folded in)

- **Probe loop (auth):** replace `_probe_tracker`/`_probe_forms`/`_probe_wiki` with one
  `_probe(service, client, identity_getter)` driven by a `[(name, client, getter)]` table
  (tracker→`login`, wiki→`username`, forms→`email`).
- **`scripts/new_endpoint.py`:** fix the CLI template to emit the post-refactor pattern
  (`app = AppContext.from_typer_context(ctx); Serializer.serialize(result, app.strategy,
  app.console)`) with the right imports; ensure scaffolded models inherit `ApiModel` and (for
  list endpoints) wire a `PaginationStrategy`.
- **Wiki `_models.py`:** add it (mirroring tracker/forms) so the three inline `_Lenient`
  copies collapse into the shared `ApiModel` (with `populate_by_name=True`).
- **Type-alias dedupe:** `KeyArg` (tracker, 4 copies, one with drifted help text) → a single
  `tracker/_args.py`; `SurveyIdArg` (forms, 3 copies) → `forms/_args.py`.
- **`RO` MCP-annotation dict** (tripled across the three `_deps.py`) → one shared definition.
- **Callback-anchor naming:** standardize the `@app.callback()` group anchor name + docstring
  (`_group` with the lazy-DI rationale) across resources; update the scaffold template.

## File structure (high level)

- Create: `src/ycli/context.py` (`AppContext`), `src/ycli/models.py` (`ApiModel` base),
  `src/ycli/yandex/pagination.py` (`PaginationStrategy` + concrete strategies),
  `src/ycli/yandex/wiki/_models.py`, `src/ycli/yandex/{tracker,forms}/_args.py`.
- Modify: `output.py` (`Serializer` + `SerializationStrategy` strategies absorb
  helpers), `transport.py` (inline header, `base=` session), `base.py` (drop `FromEnvSession`),
  the three composition-root `client.py` (raw-arg constructor), every `models.py` (inherit
  `ApiModel`), every list `client.py` (use a strategy) + list `cli.py`/`mcp.py` (`--limit`/`--all`,
  drop `--cursor`), `cli.py` (`AppContext`), `mcp.py` (`lifespan`), the three `_deps.py`
  (read lifespan context), `auth.py` (probe loop + own carve-out), `settings.py` (`max_items`),
  `scripts/new_endpoint.py`, `ARCHITECTURE.md` + `tests/test_architecture.py`.
- Delete: `src/ycli/cliformat.py`, the three `_clideps.py`, the `FromEnvSession` mixin.

## Sequencing (for the plan)

On `feat/round-2-refactor`, subagent-driven. Foundations first so each phase stays green:

1. **`ApiModel` base + `Serializer`/`SerializationStrategy` absorb the output helpers**
   (`output.py` + new `models.py`), models inherit `ApiModel`, the top-level `render()` and its
   helpers are removed, call sites become `Serializer.serialize(result,
   SerializationStrategy.from_format(cliformat.output_format(ctx)), Console())` — reusing the
   existing `cliformat.output_format(ctx)` helper from v0.6.0 (still present at this point) so
   this phase needs no AppContext yet.
2. **`AppContext` + DI overhaul:** raw-arg composition-root clients, `AppContext`
   (output_format + console + strategy + lazy clients), delete
   `from_env`/`FromEnvSession`/`_clideps`/`cliformat`, MCP `lifespan`, `auth` carve-out. Call
   sites swap `SerializationStrategy.from_format(cliformat.output_format(ctx))` → `app.strategy`
   (and `Console()` → `app.console`) and `…_client(ctx)` → `app.tracker`.
3. **`YCLI_MAX_ITEMS`** in `AppConfig`.
4. **`PaginationStrategy`** + convert each list endpoint to bounded auto-pagination returning
   `RootModel` collections; CLI `--limit`/`--all`; snapshots.
5. **Cleanups** (probe loop, `_args.py`, `_models.py`, `RO`, scaffold, naming).
6. **ARCHITECTURE.md + checks** updated to ARCH-4(new)/7/8/9/10 in this same branch.

Then PR → review → merge as `feat:` → v0.7.0 → verify PyPI → post-release `uv lock` chore.

## Out of scope

- Async / aiohttp / httpx; replacing uplink.
- The read/write MCP server (a future milestone; ARCH-3 stays until then).
- Track D (SEO) and Track E (LangChain/OpenAI schema export).
