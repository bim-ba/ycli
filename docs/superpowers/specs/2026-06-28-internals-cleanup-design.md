# Internals Cleanup — Design

> Status: approved design, ready for an implementation plan.
> Fourth code track, after A (guardrails, v0.3.0), B (AI-infra hardening, v0.4.0), and
> C (UX quick-wins, v0.5.0). Lands as `feat:` → **v0.6.0**.

## Goal

Modernize ycli's configuration and internal structure without changing the public CLI/MCP
behavior: declarative env-driven settings (`pydantic-settings`), a simpler transport, an
object-oriented `output.py` with no module global, a properly-homed multi-service `auth`,
and a `cli.py` that only mounts. Every item ships with a test (TDD) and respects the six
ARCH invariants.

## Decisions already taken (do not relitigate)

- **Stay synchronous on `requests`.** No async, no aiohttp, no httpx. Rationale: uplink
  has been dormant since March 2022 and never supported httpx; httpx itself is
  semi-abandoned (maintainer closed community participation, no stable since Dec 2024);
  the CLI is one-command-one-call and the read-only MCP gains little from async. Replacing
  dormant uplink is a possible *future* separate track — explicitly out of scope here.
- **`output.py` gets Strategy classes internally**, NOT serialize() methods on models.
  `render()` stays the single public entry so ARCH-4 and "`model_dump_json` only in
  output.py" both hold; domain models stay pure pydantic.
- **`auth` becomes a module** (`src/ycli/yandex/auth.py`) that probes all three services;
  it is CLI-only (no MCP auth tool).

## Global constraints (every task inherits these)

- **Full, self-documenting names.** No abbreviations in any new name — variables,
  fields, params, files, and especially environment variables. New env vars are
  `YCLI_TIMEOUT_SECONDS`, `YCLI_RETRIES`, `YCLI_LOG_LEVEL` (never `_S` / `_TOTAL`).
  Existing external contracts (`YANDEX_ID_OAUTH_TOKEN`, `YANDEX_ID_ORGANIZATION_ID`) keep
  their exact names — they are a published interface.
- **No hand-edited dependency lists.** Add `pydantic-settings` with `uv add pydantic-settings`.
- **ARCH invariants hold** (`tests/test_architecture.py`, `lint-imports`, `tests/test_snapshots.py`):
  HTTP only in transport/`client.py`; no `requests`/`uplink` in cli/mcp/models; `fastmcp`
  only in mcp; CLI output only via `render`; MCP tools read-only; every resource dir has
  the five canonical files; `model_dump_json` only in `output.py`.
- **New resources via `/new-endpoint`.** The new `wiki me` resource is scaffolded with
  `scripts/new_endpoint.py wiki me`, then filled — do not hand-build the five files.
- **Snapshots are intentional.** `wiki me` adds `ycli wiki me` and the `wiki_me_get` tool;
  regenerate `tests/snapshots/` with `uv run python -m tests.snapshots --update` and treat
  the diff as a reviewed artifact (ARCH-6).
- **100% coverage stays green.** Every new branch ships with a test (`--cov-fail-under=100`).
- **Conventional Commits.** Branch squash-merges as **`feat:`** → minor bump to **v0.6.0**.
- **Branch → PR → explicit approval before merge.** Never write a CI-skip token /
  `skip-checks` trailer in any commit or squash message.
- **Post-release chore:** after v0.6.0 publishes, run `uv lock` + a `build:` commit to
  resync the lockfile (PSR leaves it behind — memory `ycli-uvlock-drifts-after-each-release`).

## Items

### 1. Configuration layer — `pydantic-settings`

New `src/ycli/yandex/settings.py` holds **two single-purpose settings models**. They are
split deliberately: **app config must be constructible without credentials**, because the
root CLI callback configures logging on *every* invocation (including `ycli --help` and
credential-free `--help` on subcommands). Putting required credentials in the same model
the callback reads at startup would make every such invocation raise. Credentials are
required only when an actual API call is made.

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    """Process-wide app configuration — always constructible, never needs credentials."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    timeout_seconds: float = Field(default=30.0, validation_alias="YCLI_TIMEOUT_SECONDS")
    retries: int = Field(default=3, validation_alias="YCLI_RETRIES")
    log_level: str = Field(default="INFO", validation_alias="YCLI_LOG_LEVEL")

class Credentials(BaseSettings):
    """Yandex 360 credentials — required; pydantic raises if either env var is absent."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    oauth_token: str = Field(validation_alias="YANDEX_ID_OAUTH_TOKEN")
    organization_id: str = Field(validation_alias="YANDEX_ID_ORGANIZATION_ID")
```

`Credentials` fields have **no defaults**, so pydantic enforces presence natively —
`Credentials()` with a missing variable raises `pydantic.ValidationError`. There is **no
hand-written `require_credentials()` method** — validation is pydantic's job. The old
`os.environ.get` checks in `base.session_from_env` and `authcli` are deleted.

`.env` support: `env_file=".env"` requires `python-dotenv`, which `pydantic-settings` does
not always pull transitively — the plan verifies a `.env` is actually read by a test and
adds `python-dotenv` via `uv add` if needed. This newly auto-loads `.env` for the CLI
(today nothing does), which is the intended MCP-friendly behavior; `.env` stays gitignored.

**Tests:** `AppConfig()` returns the documented defaults when unset and reads each `YCLI_*`
override; `Credentials()` reads both `YANDEX_ID_*` vars; `Credentials()` raises
`ValidationError` when either is unset; a `.env` file is honored.

### 2. Transport simplification

In `src/ycli/yandex/transport.py`:

- `ORG_HEADER` ClassVar → a module-level constant `ORGANIZATION_HEADER = "X-Org-Id"`
  (it is a true constant — single canonical case-insensitive header per RFC 9110).
- Drop the `TIMEOUT_S` / `RETRY_TOTAL` ClassVars. `Transport.session` gains explicit
  parameters: `session(*, token, organization_id, timeout_seconds, retries)`.
- `_raise_typed`'s `if`-chain → a `match` on the status code:

```python
match code:
    case _ if code < 400:
        return response
    case 401 | 403:
        raise YandexAuthError(message, status=code, url=url)
    case 404:
        raise YandexNotFoundError(message, status=code, url=url)
    case 429:
        raise YandexRateLimitError(message, status=code, url=url)
    case _ if code >= 500:
        raise YandexServerError(message, status=code, url=url)
    case _:
        raise YandexClientError(message, status=code, url=url)
```

**Eliminate the top-level `session_from_env()` (#2).** There are four `from_env`
constructors today — `BaseYandex` plus the three composition-root clients (`TrackerClient`
/ `WikiClient` / `FormsClient`), which are not `uplink.Consumer`s and so can't inherit
`BaseYandex.from_env`. Rather than a shared top-level function, provide **one** `from_env`
classmethod via a small mixin that all four inherit, in `src/ycli/yandex/settings.py`:

```python
class FromEnvSession:
    """Mixin: `from_env()` builds an authed session from the environment and injects it.

    Inherited by BaseYandex and the three composition-root clients; each defines its own
    `__init__(*, session: requests.Session)`, so `cls(session=...)` constructs correctly.
    """

    @classmethod
    def from_env(cls) -> Self:
        credentials = Credentials()  # raises ValidationError if a var is missing
        config = AppConfig()
        session = Transport.session(
            token=credentials.oauth_token,
            organization_id=credentials.organization_id,
            timeout_seconds=config.timeout_seconds,
            retries=config.retries,
        )
        return cls(session=session)
```

- `base.py`: `BaseYandex(FromEnvSession, uplink.Consumer)`; its bespoke `from_env` and the
  top-level `session_from_env()` are deleted.
- The three composition roots add `FromEnvSession` as a base and **delete their own
  `from_env`** (they inherit the mixin's). Each keeps its `__init__(*, session)` that fans
  the one session out to its sub-clients — so a `TrackerClient.from_env()` still builds
  exactly one session shared across all tracker resources.
- ARCH / import-linter: `settings.py` imports `Transport` and reads the env; it constructs
  no HTTP itself (delegates to `Transport`, which stays env-free — it must never import
  `settings`). Confirm `lint-imports` stays green; if the mixin's location trips a layering
  rule, place `FromEnvSession` in `base.py` instead (it already sits at that layer) and
  import `Credentials`/`AppConfig` from `settings.py`.

**Tests:** `Transport.session` applies the passed `timeout_seconds`/`retries`; the `match`
mapping keeps the same status→exception behavior (extend `tests/yandex/test_errors.py`);
`from_env` raises `ValidationError` when a credential is unset (no HTTP call), for both a
resource client and a composition root.

### 3. `output.py` — Strategy classes, no module global

Refactor the functional renderer into a small strategy hierarchy *inside* `output.py`:

```python
class SerializationStrategy(ABC):
    @abstractmethod
    def serialize(self, result: BaseModel, console: Console) -> None: ...

class JsonStrategy(SerializationStrategy): ...
class YamlStrategy(SerializationStrategy): ...
class PrettyStrategy(SerializationStrategy): ...   # owns _prettify / table helpers + key links
class AutoStrategy(SerializationStrategy):
    """Delegates to Pretty on a TTY, Json when piped."""
```

- `render(result, *, output_format, console=None)` becomes the single public entry: it maps
  the `OutputFormat` to a strategy and calls `serialize`. ARCH-4 holds; `model_dump_json`
  stays inside this module (in `JsonStrategy`).
- **Kill the `global _format`.** The format is threaded explicitly:
  - the root CLI callback stores the chosen `OutputFormat` on the typer `Context`
    (`ctx.obj` already carries the per-domain client — extend it, or use a small dataclass
    `CliState(output_format, client)`), and
  - each command passes `output_format` into `render(...)`.
  - `set_format` / module `_format` are removed.
- The existing key-link behavior (OSC8 on Tracker keys, TTY-gated) moves into
  `PrettyStrategy` unchanged.

This is internal-only: CLI output bytes are identical for every format. The `_clideps`/
`_deps` context objects and every domain `cli.py` command call site update to pass the
format through (mechanical, wide — but covered by existing CLI tests + snapshots).

**Tests:** existing `tests/test_output_links.py` and any format tests keep passing
unchanged in observable output; add a unit test per strategy (`JsonStrategy` emits pristine
JSON when piped, `PrettyStrategy` emits the table + key link on a forced-terminal console,
`AutoStrategy` picks Pretty vs Json by `console.is_terminal`). No `global` remains (a grep
assertion in `tests/test_architecture.py` is reasonable but optional).

### 4. `auth` → `src/ycli/yandex/auth.py` + new `wiki me` resource

**New `wiki me` resource** (scaffold `scripts/new_endpoint.py wiki me`, then fill):

- `client.py` — `MeClient(WikiResource)` with `get()` → `@uplink.get("users/me")` → `Me`.
- `models.py` — `Me(BaseModel)` for `GET /v1/users/me`: `username`, nested `identity`
  (`uid`, `cloud_uid`), nested `org` (`dir_id`, `collab_id`) with aliases as returned.
- `cli.py` — `ycli wiki me` → `render(wiki_client(ctx).me.get(), output_format=...)`.
- `mcp.py` — tool `me_get`, `annotations={**RO, "title": "Get current Wiki user"}`.
- Register: `self.me = MeClient(session=session)` in `wiki/client.py`; `add_typer` in
  `wiki/cli.py`; `mcp.mount` in `wiki/mcp.py`. Completes four-surface `me` symmetry across
  Tracker / Wiki / Forms.

**`src/ycli/yandex/auth.py`** — a cross-cutting module (it sits above the three domains and
imports their clients; it is not a resource, so the five-file rule does not apply):

- `ServiceAuthStatus(BaseModel)`: `service: str`, `valid: bool`, `login: str | None`,
  `detail: str`.
- `AuthReport(BaseModel)`: `configured: bool`, `organization_id: str`,
  `services: list[ServiceAuthStatus]`. Rendered via `render` (ARCH-4).
- A probe function maps each service to its identity call:
  `tracker` → `TrackerClient.from_env().me.get()` (`.login`/`.display`),
  `forms` → `FormsClient.from_env().me.get()`,
  `wiki` → `WikiClient.from_env().me.get()` (`.username`). Each probe is wrapped: a caught
  `YandexAuthError` → `valid=False, detail="token invalid or expired"`; other `YandexError`
  → `valid=False, detail=str(exc)`; success → `valid=True` with the identity.
- A small `auth` Typer app (`status` command) lives in this module: it constructs
  `Credentials()` inside a `try` — on `ValidationError` it reports `configured=False` +
  non-zero exit (no HTTP), naming the missing variable(s) from the error; otherwise it
  builds the `AuthReport` across all three services. Overall exit code is non-zero if any
  probed service is invalid.
- Delete `src/ycli/authcli.py`; `cli.py` imports the `auth` app from `yandex.auth`.

**Tests:** with `responses` stubbing each `/me` endpoint — all-valid → `AuthReport` with
three `valid=True`; one 401 → that service `valid=False`, others valid, non-zero exit;
missing env → `configured=False`, non-zero exit, no HTTP. Plus the `wiki me` resource's own
client/cli/mcp tests, mirroring `tracker me`.

### 5. `mcp` launcher out of `cli.py`

Move the `ycli mcp` command body into a small dedicated module (e.g.
`src/ycli/mcp_launcher.py`) that lazy-imports `ycli.mcp` (so it stays importable without the
`mcp` extra) and exposes the command function. `cli.py` registers it
(`app.command(name="mcp")(launch_mcp_server)`) so `cli.py` is back to pure mounting +
registration. Behavior and the "requires the mcp extra" error are unchanged.

Additionally, `cli.py`'s `main()` wrapper catches `pydantic.ValidationError` (raised by
`from_env` when a credential is missing) alongside the existing `YandexError`, printing the
same one-line `Error: ...` naming the missing variable instead of a traceback — so a
credential-less API command stays friendly now that the missing-var check is pydantic's.

**Tests:** the existing `test_mcp_subcommand_launches_server` keeps passing (adjust the
monkeypatch target to the new module); the missing-extra path still raises the friendly
`BadParameter`; a credential-less API command prints the friendly `Error:` line (no
traceback).

## File structure (created / modified)

- Create: `src/ycli/yandex/settings.py`, `src/ycli/yandex/auth.py`,
  `src/ycli/mcp_launcher.py`, `src/ycli/yandex/wiki/me/{__init__,models,client,cli,mcp}.py`.
- Modify: `transport.py` (constant, params, `match`), `base.py` (drop `session_from_env`,
  settings-based `from_env`), `output.py` (strategies, drop global), `cli.py` (mounting +
  mcp registration + format threading), each domain `cli.py`/`_clideps`/`_deps`
  (format threading), `wiki/{client,cli,mcp}.py` (register `me`), `pyproject.toml`
  (via `uv add`).
- Delete: `src/ycli/authcli.py`.
- Snapshots: `tests/snapshots/cli_tree.txt` (+`wiki me`), `tests/snapshots/mcp_tools.txt`
  (+`wiki_me_get`).

## Sequencing (for the plan)

On `feat/internals-cleanup` (already created off main @ v0.5.0), subagent-driven like A/B/C.
Order so foundations land first and the wide mechanical change is isolated:

1. **`pydantic-settings` settings module** (`uv add` + `YandexSettings` + tests).
2. **Transport + base refactor** (constant, params, `match`, settings-based `from_env`,
   delete `session_from_env`).
3. **`output.py` strategies + drop the global** (+ thread format through Context; widest
   mechanical edit — isolate it).
4. **`wiki me` resource** via `/new-endpoint`, filled + registered + snapshot.
5. **`auth.py`** (depends on `wiki me` + the C-era `me` resources + typed errors); delete
   `authcli.py`.
6. **`mcp` launcher relocation.**

Then PR → review → merge as `feat:` → v0.6.0 → verify PyPI → post-release `uv lock` chore.

## Out of scope

- Async / aiohttp / httpx migration and any replacement of uplink (possible future track).
- Serialize() methods on domain models (rejected — would invert ARCH-4).
- An MCP auth tool (auth stays CLI-only; MCP remains read-only domain tools).
- Track D (SEO) and Track E (LangChain/OpenAI schema export) — separate tracks.
