# Round-2 Architecture Refactor — Design

> Status: approved design, ready for an implementation plan.
> Fifth track, after A (guardrails, v0.3.0), B (AI-infra, v0.4.0), C (UX, v0.5.0), and the
> internals-cleanup track (v0.6.0). Lands as `feat:` → **v0.7.0**.

## Goal

Make ycli's internals match the design principles the maintainer has repeatedly asked for:
clean **dependency injection** (clients never read the environment), **self-serializing
models**, and **encapsulated pagination** — so the public surface (CLI, MCP, importable SDK)
is simpler and scales. No new endpoints; behavior changes are limited to the deliberate ones
below (pagination ergonomics, friendlier SDK construction). The architecture invariants are
updated to encode the new principles.

## Decisions already taken (do not relitigate)

- **Composition-root DI.** Clients receive their credentials/session via the constructor and
  never read `os.environ`. The environment is read once at a composition root (the CLI
  `AppContext`, the MCP `lifespan`). `FromEnvSession` and every `from_env` are deleted.
- **Public SDK clients take `credentials`, not a raw session.** The three composition-root
  clients (`TrackerClient`/`WikiClient`/`FormsClient`) — the public SDK entry points — accept
  `credentials: Credentials` (+ optional `config: AppConfig`, + an optional pre-built `session`
  for advanced injection). Leaf resource clients take `session` only. (Mirrors the OpenAI
  Python SDK's three-tier layering: public client = credentials, optional `http_client`
  injection, internal transport.)
- **Typed `AppContext`** replaces the `cliformat.output_format(ctx)` helper: one typed object
  on `ctx.obj` holding `output_format` + the lazily-built session/domain-clients, with a
  `from_typer_context` classmethod for typed retrieval.
- **Self-serializing models.** `SerializableModel` / `SerializableRootModel` base with
  `.serialize(output_format, console=None)`; the format strategies stay in `output.py` and
  absorb the top-level helpers. Replaces ARCH-4.
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

- **ARCH-4 — Self-serializing models (replaces "Output discipline").** Every API model
  inherits `SerializableModel` or `SerializableRootModel`; rendering happens via
  `model.serialize(output_format)`; the serialization strategies live only in
  `src/ycli/output.py` (`model_dump_json` stays confined there). *Check:* models subclass the
  base; `model_dump_json` only in `output.py`.
- **ARCH-7 — Composition-root dependency injection (new).** Clients receive their
  dependencies via the constructor; **credentials are always injected, never resolved from
  the environment inside a client**. There is no `from_env` on any client. *Check:* grep —
  no `os.environ`, no `from_env`, no `Credentials(` inside `yandex/**/client.py` or `base.py`.
  (A composition-root client MAY default app settings via `AppConfig()` — non-sensitive
  defaults — but must never construct `Credentials()`; the security boundary is credentials.)
- **ARCH-8 — Single configuration source (new).** No direct `os.environ` access and no
  `BaseSettings` *subclass definition* outside `src/ycli/yandex/settings.py`; other modules
  obtain configuration by *instantiating* the settings models (`Credentials()` / `AppConfig()`).
  *Check:* grep — `os.environ` and `class …(BaseSettings)` appear only in `settings.py`.
- **ARCH-9 — Typed boundary errors (new).** Non-2xx responses raise a typed `YandexError`
  subclass from the transport hook; no surface parses an error body into a model. *Check:*
  the existing status→exception mapping test, plus no `raise_for_status` / status-branching
  outside `transport.py`.
- **ARCH-10 — No shadowing of configurable values (new).** A value backed by settings
  (timeout, retries, max-items, log level) is not hardcoded at a call site. *Check:* grep —
  no `@uplink.timeout`, no literal page-size/`max_items` defaults duplicated outside
  `settings.py`.

## Items

### 1. Configuration — add `YCLI_MAX_ITEMS`

`AppConfig` (in `settings.py`) gains `max_items: int = Field(default=500,
validation_alias="YCLI_MAX_ITEMS")`. This is the default pagination cap.

### 2. Dependency-injection overhaul

**`transport.py`:** inline the org header (`"X-Org-Id"`) at its one use site (drop the
`ORGANIZATION_HEADER` constant). `Transport.session` stays env-free and parameterized.

**Leaf resource clients** (`yandex/**/<resource>/client.py`): unchanged constructor —
`__init__(*, session)`. They never read env (already true once `from_env` is gone).

**Composition-root clients** (`tracker/client.py`, `wiki/client.py`, `forms/client.py`) —
the public SDK entry points:

```python
class TrackerClient:
    def __init__(
        self,
        *,
        credentials: Credentials | None = None,
        config: AppConfig | None = None,
        session: requests.Session | None = None,
    ) -> None:
        if session is None:
            if credentials is None:
                raise ValueError("pass credentials= or a pre-built session=")
            config = config or AppConfig()
            session = Transport.session(
                token=credentials.oauth_token,
                organization_id=credentials.organization_id,
                timeout_seconds=config.timeout_seconds,
                retries=config.retries,
            )
        self.issues = IssuesClient(session=session)
        ...  # fan the one session out to all sub-clients
```

No `from_env`. `FromEnvSession` is deleted; `BaseYandex` loses it. `Transport.session` build
moves out of `base.py` into the composition-root constructors (the only place that turns
credentials into a session). `settings.py` no longer needs the `FromEnvSession` mixin.

**CLI composition root — `AppContext`.** New `src/ycli/context.py`:

```python
@dataclass
class AppContext:
    output_format: OutputFormat
    _credentials: Credentials | None = None      # resolved lazily on first client access
    _config: AppConfig | None = None
    _clients: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_typer_context(cls, ctx: typer.Context) -> "AppContext":
        """Return the AppContext stored on ctx.obj (built by the root callback)."""
        return ctx.obj

    def _client(self, domain, factory):
        if domain not in self._clients:
            self._credentials = self._credentials or Credentials()  # raises if unset
            self._clients[domain] = factory(credentials=self._credentials, config=self._config)
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
context manager that builds the three clients once at startup from `Credentials()`/`AppConfig()`
and yields them; the three `_deps.py` provider functions read `ctx.lifespan_context[...]`
instead of calling `from_env()`. (Confirm the installed fastmcp version's `lifespan`/Context
API during planning; fastmcp 3.4.2 supports `lifespan=` and `ctx.lifespan_context`.)

**`auth.py`** keeps its own credential carve-out: it constructs `Credentials()` directly to
report "not configured", and builds the three clients from those credentials (not via
`AppContext`, since `auth status` must run credential-free up to the point of reporting).

### 3. Serialization — `SerializableModel`

New base (in `src/ycli/output.py`, so `model_dump_json` stays confined):

```python
class SerializableModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    def serialize(self, output_format: OutputFormat, console: Console | None = None) -> None:
        _STRATEGIES[output_format]().serialize(self, console or Console())

class SerializableRootModel(RootModel[T]):   # generic; same serialize() method
    ...
```

- The strategies (`JsonStrategy`/`YamlStrategy`/`PrettyStrategy`/`AutoStrategy`) absorb the
  top-level helpers: `_prettify`/`_kv_table`/`_list_table`/`_cell`/`_key_link`/`_KEY_RE`
  become methods/attributes of `PrettyStrategy`. The top-level `render()` and
  `cliformat.output_format` are removed; `cliformat.py` is deleted.
- The four scattered `_Lenient` bases (tracker, forms, two inline copies in wiki) consolidate
  into `SerializableModel`. Every `models.py` class inherits `SerializableModel`; every
  `XList(RootModel[...])` becomes `XList(SerializableRootModel[...])`.
- Command bodies become `AppContext.from_typer_context(ctx).tracker.issues.get(key)
  .serialize(app.output_format)`.

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
`strategy.collect(fetch_page, limit)`, and returns a `SerializableRootModel` collection
(`Users`-style). The per-page envelope models (`DescendantsResponse`, `AnswersResponse`,
`SurveyList`, …) become **internal** parse types (used inside the client to read one page),
not public return types.

Bound: `limit` defaults to `AppConfig.max_items` (`YCLI_MAX_ITEMS`). CLI list commands expose
`--limit N` (override the cap) and `--all` (uncapped, `limit=None`), replacing `--cursor`. MCP
list tools use the default cap (no cursor parameter); their descriptions state the cap.

### 5. Cleanups (folded in)

- **Probe loop (auth):** replace `_probe_tracker`/`_probe_forms`/`_probe_wiki` with one
  `_probe(service, client, identity_getter)` driven by a `[(name, client, getter)]` table
  (tracker→`login`, wiki→`username`, forms→`email`).
- **`scripts/new_endpoint.py`:** fix the CLI template to emit `.serialize(app.output_format)`
  (the post-refactor pattern) and the `AppContext` import; ensure the scaffolded client/models
  inherit the new bases and (for list endpoints) wire a `PaginationStrategy`.
- **Wiki `_models.py`:** add it (mirroring tracker/forms) so the three inline `_Lenient`
  copies collapse into the shared `SerializableModel` (with `populate_by_name=True`).
- **Type-alias dedupe:** `KeyArg` (tracker, 4 copies, one with drifted help text) → a single
  `tracker/_args.py`; `SurveyIdArg` (forms, 3 copies) → `forms/_args.py`.
- **`RO` MCP-annotation dict** (tripled across the three `_deps.py`) → one shared definition.
- **Callback-anchor naming:** standardize the `@app.callback()` group anchor name + docstring
  (`_group` with the lazy-DI rationale) across resources; update the scaffold template.

## File structure (high level)

- Create: `src/ycli/context.py` (`AppContext`), `src/ycli/yandex/pagination.py`
  (`PaginationStrategy` + concrete strategies), `src/ycli/yandex/wiki/_models.py`,
  `src/ycli/yandex/{tracker,forms}/_args.py`.
- Modify: `output.py` (`SerializableModel`/`SerializableRootModel` + strategies absorb
  helpers), `transport.py` (inline header), `base.py` (drop `FromEnvSession`), the three
  composition-root `client.py` (credentials constructor), every `models.py` (inherit the new
  bases), every list `client.py` (use a strategy) + list `cli.py`/`mcp.py` (`--limit`/`--all`,
  drop `--cursor`), `cli.py` (`AppContext`), `mcp.py` (`lifespan`), the three `_deps.py`
  (read lifespan context), `auth.py` (probe loop + own carve-out), `settings.py` (`max_items`),
  `scripts/new_endpoint.py`, `ARCHITECTURE.md` + `tests/test_architecture.py`.
- Delete: `src/ycli/cliformat.py`, the three `_clideps.py`, the `FromEnvSession` mixin.

## Sequencing (for the plan)

On `feat/round-2-refactor`, subagent-driven. Foundations first so each phase stays green:

1. **`SerializableModel`/`SerializableRootModel` + strategies absorb the output helpers**
   (`output.py`), models inherit the base, the top-level `render()` and its helpers are
   removed, call sites become `model.serialize(output_format=output_format(ctx))` — reusing
   the existing `cliformat.output_format(ctx)` helper from v0.6.0 (still present at this point)
   so this phase needs no AppContext yet.
2. **`AppContext` + DI overhaul:** credentials-based composition-root clients, `AppContext`
   (output_format + lazy clients), delete `from_env`/`FromEnvSession`/`_clideps`/`cliformat`,
   MCP `lifespan`, `auth` carve-out. Call sites swap `output_format(ctx)` →
   `AppContext.from_typer_context(ctx).output_format` and `…_client(ctx)` → `app.tracker`.
3. **`YCLI_MAX_ITEMS`** in `AppConfig`.
4. **`PaginationStrategy`** + convert each list endpoint to bounded auto-pagination returning
   `SerializableRootModel` collections; CLI `--limit`/`--all`; snapshots.
5. **Cleanups** (probe loop, `_args.py`, `_models.py`, `RO`, scaffold, naming).
6. **ARCHITECTURE.md + checks** updated to ARCH-4(new)/7/8/9/10 in this same branch.

Then PR → review → merge as `feat:` → v0.7.0 → verify PyPI → post-release `uv lock` chore.

## Out of scope

- Async / aiohttp / httpx; replacing uplink.
- The read/write MCP server (a future milestone; ARCH-3 stays until then).
- Track D (SEO) and Track E (LangChain/OpenAI schema export).
