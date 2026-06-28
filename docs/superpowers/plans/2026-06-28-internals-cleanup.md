# Internals Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize ycli's configuration and internal structure (env-driven `pydantic-settings`, simpler transport, OO `output.py` with no module global, a properly-homed multi-service `auth`, a mount-only `cli.py`) with zero change to public CLI/MCP behavior.

**Architecture:** Two `pydantic-settings` models (`AppConfig` always-constructible, `Credentials` required) feed a single `from_env` mixin that all client constructors inherit; the transport keeps HTTP knowledge and gains explicit `timeout_seconds`/`retries`; `output.py` becomes a small Strategy hierarchy behind the single `render()` entry, with the format threaded from the typer Context instead of a global; `auth` moves to `src/ycli/yandex/auth.py` and probes Tracker/Wiki/Forms via their `me` resources (a new `wiki me` completes the trio).

**Tech Stack:** Python ≥3.12, uv, pydantic + pydantic-settings, typer, uplink + requests (sync), fastmcp, rich, loguru, pytest + responses.

**Spec:** `docs/superpowers/specs/2026-06-28-internals-cleanup-design.md`

## Global Constraints

- **Full, self-documenting names — no abbreviations.** New env vars are exactly `YCLI_TIMEOUT_SECONDS`, `YCLI_RETRIES`, `YCLI_LOG_LEVEL`. Existing `YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID` keep their names (published interface).
- **No hand-edited dependency lists.** Runtime deps via `uv add`, dev via `uv add --dev`.
- **Stay synchronous on `requests`.** No async / aiohttp / httpx; do not replace uplink.
- **`output.py` keeps `render()` as the single public entry** (ARCH-4) and remains the only place calling `model_dump_json` — no `serialize()` on domain models.
- **MCP server stays read-only.** `auth` is CLI-only (no MCP auth tool).
- **ARCH invariants hold** (`tests/test_architecture.py`, `uv run lint-imports`, `tests/test_snapshots.py`): HTTP only in transport/`client.py`; no `requests`/`uplink` in cli/mcp/models; `fastmcp` only in mcp; CLI output only via `render`; MCP tools read-only; every resource dir has the five canonical files; `model_dump_json` only in `output.py`.
- **New resources via `/new-endpoint`.** The new `wiki me` resource is scaffolded with `python scripts/new_endpoint.py wiki me`, then filled — never hand-built.
- **Snapshots are intentional.** Regenerate with `uv run python -m tests.snapshots --update`; treat the diff as a reviewed artifact (ARCH-6).
- **100% coverage stays green.** `uv run pytest` enforces `--cov-fail-under=100`; every new branch ships with a test.
- **Conventional Commits.** Per-task commits use `feat:` / `refactor:` / `test:` as fits; the branch squash-merges as `feat:` → **v0.6.0**.
- **Never write a CI-skip token** (`[skip ci]` etc.) or `skip-checks` trailer in any commit/squash message.
- **Verification before done:** run `uv run pytest` and `uv run lint-imports` and confirm output before claiming a task complete.

---

### Task 1: `pydantic-settings` configuration models

**Files:**
- Create: `src/ycli/yandex/settings.py`
- Modify: `pyproject.toml` (via `uv add`, not by hand), `src/ycli/cli.py:34-36` (wire log level)
- Test: `tests/yandex/test_settings.py`

**Interfaces:**
- Produces: `AppConfig` (BaseSettings; fields `timeout_seconds: float = 30.0`, `retries: int = 3`, `log_level: str = "INFO"`), `Credentials` (BaseSettings; required fields `oauth_token: str`, `organization_id: str`). Both read `.env` and the environment; `Credentials()` raises `pydantic.ValidationError` when a var is unset.

- [ ] **Step 1: Add the dependency**

Run: `uv add pydantic-settings`
Expected: `pyproject.toml` gains `pydantic-settings` under `[project] dependencies`; `uv.lock` updates.

- [ ] **Step 2: Write the failing tests**

Create `tests/yandex/test_settings.py`:

```python
"""Settings models — env-driven config with required credentials."""
import pytest
from pydantic import ValidationError

from ycli.yandex.settings import AppConfig, Credentials


def test_app_config_defaults(monkeypatch):
    for var in ("YCLI_TIMEOUT_SECONDS", "YCLI_RETRIES", "YCLI_LOG_LEVEL"):
        monkeypatch.delenv(var, raising=False)
    config = AppConfig()
    assert config.timeout_seconds == 30.0
    assert config.retries == 3
    assert config.log_level == "INFO"


def test_app_config_reads_overrides(monkeypatch):
    monkeypatch.setenv("YCLI_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("YCLI_RETRIES", "7")
    monkeypatch.setenv("YCLI_LOG_LEVEL", "DEBUG")
    config = AppConfig()
    assert config.timeout_seconds == 12.5
    assert config.retries == 7
    assert config.log_level == "DEBUG"


def test_credentials_read_env(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    creds = Credentials()
    assert creds.oauth_token == "tok"
    assert creds.organization_id == "org"


def test_credentials_missing_raises(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    with pytest.raises(ValidationError):
        Credentials()


def test_settings_read_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("YCLI_LOG_LEVEL", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("YCLI_LOG_LEVEL=WARNING\n")
    assert AppConfig().log_level == "WARNING"
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/yandex/test_settings.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ycli.yandex.settings'`.

- [ ] **Step 4: Implement the settings module**

Create `src/ycli/yandex/settings.py`:

```python
"""Env-driven configuration — two single-purpose pydantic-settings models.

Split deliberately: app config must be constructible WITHOUT credentials (the root CLI
callback configures logging on every invocation, including ``--help``), while credentials
are required only when an API call is made. ``Credentials`` has no defaults, so pydantic
enforces presence — no hand-written validation.
"""
from __future__ import annotations

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

- [ ] **Step 5: Run the tests; if `.env` test fails, add python-dotenv**

Run: `uv run pytest tests/yandex/test_settings.py -v`
Expected: PASS. If `test_settings_read_dotenv` fails with a hint that dotenv support is missing, run `uv add python-dotenv`, then re-run — Expected: PASS.

- [ ] **Step 6: Wire the configurable log level into the CLI callback**

In `src/ycli/cli.py`, the root callback currently calls `configure()`. Make it use `AppConfig().log_level` (this is also the first real consumer of `AppConfig`). Replace the callback body so it reads:

```python
from ycli.yandex.settings import AppConfig
...
@app.callback()
def _main(
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", "-o", help="Output format (auto = pretty on a TTY, JSON when piped)."),
    ] = OutputFormat.auto,
) -> None:
    """Configure logging and the output format before any subcommand runs."""
    configure(level=AppConfig().log_level)
    set_format(output_format)
```

(`set_format` stays for now; it is removed in Task 6.)

- [ ] **Step 7: Add a CLI log-level test**

Append to `tests/yandex/test_settings.py`:

```python
def test_cli_callback_uses_configured_log_level(monkeypatch):
    import ycli.cli as cli
    captured = {}
    monkeypatch.setenv("YCLI_LOG_LEVEL", "ERROR")
    monkeypatch.setattr("ycli.cli.configure", lambda level: captured.setdefault("level", level))
    from typer.testing import CliRunner
    CliRunner().invoke(cli.app, ["--help"])
    assert captured["level"] == "ERROR"
```

- [ ] **Step 8: Run the full suite + lint**

Run: `uv run pytest -q && uv run lint-imports`
Expected: all pass, 100% coverage, `lint-imports` "Contracts: N kept, 0 broken".

- [ ] **Step 9: Commit**

```bash
git add src/ycli/yandex/settings.py tests/yandex/test_settings.py src/ycli/cli.py pyproject.toml uv.lock
git commit -m "feat: env-driven settings (AppConfig, Credentials) via pydantic-settings

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Transport simplification + `FromEnvSession` mixin

**Files:**
- Modify: `src/ycli/yandex/transport.py` (constant, params, `match`), `src/ycli/yandex/base.py` (mixin, drop `session_from_env`), `src/ycli/yandex/tracker/client.py`, `src/ycli/yandex/wiki/client.py`, `src/ycli/yandex/forms/client.py` (inherit mixin, drop own `from_env`), `src/ycli/cli.py:62-72` (catch `ValidationError`)
- Test: `tests/yandex/test_transport.py` (existing — update), `tests/yandex/test_errors.py` (existing — keep green), add cases as below

**Interfaces:**
- Consumes: `AppConfig`, `Credentials` (Task 1).
- Produces: `Transport.session(*, token: str, organization_id: str, timeout_seconds: float, retries: int) -> requests.Session`; module constant `ORGANIZATION_HEADER = "X-Org-Id"`; `FromEnvSession` mixin with `from_env(cls) -> Self`. `session_from_env` no longer exists.

- [ ] **Step 1: Find every caller of the old surface (so nothing is missed)**

Run: `rg -n "session_from_env|ORG_HEADER|TIMEOUT_S|RETRY_TOTAL|org_id=" src tests`
Expected: a list including `base.py`, the three `client.py`, `transport.py`, and any tests. Every hit is updated in this task.

- [ ] **Step 2: Update the transport tests first (red)**

In `tests/yandex/test_transport.py`, change `Transport.session` calls to the new keyword signature and add coverage for the configured values. Replace the relevant calls/assertions with:

```python
def test_session_sets_auth_and_org_headers():
    s = Transport.session(token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    assert s.headers["Authorization"] == "OAuth t"
    assert s.headers["X-Org-Id"] == "o"


def test_session_applies_configured_timeout_and_retries():
    s = Transport.session(token="t", organization_id="o", timeout_seconds=12.5, retries=7)
    adapter = s.get_adapter("https://example.com")
    assert adapter._timeout == 12.5
    assert adapter.max_retries.total == 7


def test_session_rejects_empty_credentials():
    import pytest
    with pytest.raises(ValueError):
        Transport.session(token="", organization_id="o", timeout_seconds=30.0, retries=3)
```

Run: `uv run pytest tests/yandex/test_transport.py -v`
Expected: FAIL (old signature / `org_id`).

- [ ] **Step 3: Rewrite `transport.py`**

In `src/ycli/yandex/transport.py`:
- Replace the `ORG_HEADER` ClassVar with a module-level constant after the imports: `ORGANIZATION_HEADER = "X-Org-Id"`.
- Drop the `TIMEOUT_S` / `RETRY_TOTAL` ClassVars.
- Change `session` to take explicit params and use the constant:

```python
class Transport:
    """Builds an authed ``requests.Session`` — the single, env-free auth boundary."""

    @classmethod
    def session(
        cls,
        *,
        token: str,
        organization_id: str,
        timeout_seconds: float,
        retries: int,
    ) -> requests.Session:
        if not token:
            raise ValueError("token must be a non-empty string")
        if not organization_id:
            raise ValueError("organization_id must be a non-empty string")
        session = requests.Session()
        session.headers.update(
            {"Authorization": f"OAuth {token}", ORGANIZATION_HEADER: organization_id}
        )
        session.hooks["response"].append(_raise_typed)
        retry = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
            raise_on_status=False,
        )
        adapter = _TimeoutAdapter(max_retries=retry, timeout=timeout_seconds)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
```

- Convert `_raise_typed`'s `if`-chain to a `match` (keep `message`/`url` construction):

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

(Rename the local `snippet`/`msg` to `message` consistently, or keep `msg` — just be consistent.) Update the module docstring/doctest at the top of the file to use `organization_id=` and `X-Org-Id` (the doctest `>>> s.headers["Authorization"]` stays valid; fix any `org_id` reference).

- [ ] **Step 4: Rewrite `base.py` with the mixin, delete `session_from_env`**

Replace `src/ycli/yandex/base.py` body so it reads:

```python
import requests
import uplink
from typing import ClassVar, Self

from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.transport import Transport


class FromEnvSession:
    """Mixin: ``from_env()`` builds an authed session from the environment and injects it.

    Inherited by ``BaseYandex`` and the three composition-root clients; each defines its
    own ``__init__(*, session)``, so ``cls(session=...)`` constructs correctly. Credentials
    are validated by pydantic — a missing var raises ``pydantic.ValidationError`` here.
    """

    @classmethod
    def from_env(cls) -> Self:
        credentials = Credentials()
        config = AppConfig()
        session = Transport.session(
            token=credentials.oauth_token,
            organization_id=credentials.organization_id,
            timeout_seconds=config.timeout_seconds,
            retries=config.retries,
        )
        return cls(session=session)


class BaseYandex(FromEnvSession, uplink.Consumer):
    """Required-``session`` DI + ``from_env`` (via mixin) + ``base_url`` classvar."""

    base_url: ClassVar[str]

    def __init__(self, *, session: requests.Session) -> None:
        base = self.base_url.rstrip("/") + "/"
        self._session: requests.Session = session
        super().__init__(base_url=base, client=session)
```

(Keep the file's module docstring and the `NOTE: no from __future__ import annotations` comment — uplink reads annotations eagerly, so do NOT add that import.)

- [ ] **Step 5: Make the three composition roots inherit the mixin**

In each of `tracker/client.py`, `wiki/client.py`, `forms/client.py`:
- Replace `from ycli.yandex.base import session_from_env` with `from ycli.yandex.base import FromEnvSession`.
- Change the class declaration to inherit the mixin, e.g. `class TrackerClient(FromEnvSession):`.
- Delete the bespoke `from_env` classmethod (now inherited). Keep `__init__(*, session)` unchanged.

Example for `tracker/client.py`:

```python
from ycli.yandex.base import FromEnvSession
...
class TrackerClient(FromEnvSession):
    def __init__(self, *, session: requests.Session) -> None:
        self.me = MeClient(session=session)
        ...  # unchanged sub-client wiring
    # no from_env here — inherited from FromEnvSession
```

- [ ] **Step 6: Catch `ValidationError` at the CLI boundary**

In `src/ycli/cli.py` `main()`, a missing credential now raises `pydantic.ValidationError` from `from_env`. Extend the wrapper:

```python
def main() -> None:  # pragma: no cover
    from pydantic import ValidationError
    from ycli.yandex.errors import YandexError
    import typer
    try:
        app()
    except (YandexError, ValidationError) as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc
```

- [ ] **Step 7: Run the impacted tests, then the full suite + lint**

Run: `uv run pytest tests/yandex/test_transport.py tests/yandex/test_errors.py -v`
Expected: PASS.
Run: `uv run pytest -q && uv run lint-imports`
Expected: all pass, 100% coverage, contracts 0 broken. (If `lint-imports` flags the new `base → settings` import, that is allowed by layering; only act if a contract actually breaks.)

- [ ] **Step 8: Commit**

```bash
git add src/ycli/yandex/transport.py src/ycli/yandex/base.py \
        src/ycli/yandex/tracker/client.py src/ycli/yandex/wiki/client.py \
        src/ycli/yandex/forms/client.py src/ycli/cli.py tests/yandex/test_transport.py
git commit -m "refactor: parameterized transport + FromEnvSession mixin (drop top-level session_from_env)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: New `wiki me` resource (`GET /v1/users/me`)

**Files:**
- Create (via scaffold, then fill): `src/ycli/yandex/wiki/me/{__init__,models,client,cli,mcp}.py`
- Modify: `src/ycli/yandex/wiki/client.py` (register `self.me`), `src/ycli/yandex/wiki/cli.py` (add_typer), `src/ycli/yandex/wiki/mcp.py` (mount), `tests/snapshots/cli_tree.txt`, `tests/snapshots/mcp_tools.txt`
- Test: `tests/yandex/wiki/test_me.py` (new, mirror `tests/yandex/tracker/test_me.py`)

**Interfaces:**
- Consumes: `WikiResource` (`base_url = https://api.wiki.yandex.net/v1`), `wiki_client` (cli DI), `WikiClient`, `RO`/`TAGS` (`wiki/_deps.py`), the `FromEnvSession`-based `WikiClient.from_env` (Task 2).
- Produces: `wiki.me.get() -> Me`; CLI `ycli wiki me get`; MCP tool `wiki_me_get`. `Me` has `username`, `home_cluster`, nested `identity` (`uid`, `cloud_uid`), nested `org` (`dir_id`, `collab_id`).

- [ ] **Step 1: Scaffold the resource**

Run: `python scripts/new_endpoint.py wiki me`
Expected: creates `src/ycli/yandex/wiki/me/{__init__,client,cli,mcp,models}.py` with FILL stubs.

- [ ] **Step 2: Write the failing tests**

Create `tests/yandex/wiki/test_me.py` (mirror `tests/yandex/tracker/test_me.py`, adjusting for Wiki's `/v1/users/me` and `username`):

```python
"""Wiki /users/me resource — client, CLI, MCP."""
import pytest
import responses
from typer.testing import CliRunner

import ycli.cli as cli
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.me.models import Me

ME_URL = "https://api.wiki.yandex.net/v1/users/me"
ME_BODY = {
    "username": "alice",
    "home_cluster": "homepage",
    "identity": {"uid": "1", "cloud_uid": "c1"},
    "org": {"dir_id": "d1", "collab_id": "11111111-1111-1111-1111-111111111111"},
}


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")


@responses.activate
def test_client_get_parses_me(creds):
    responses.add(responses.GET, ME_URL, json=ME_BODY, status=200)
    me = WikiClient.from_env().me.get()
    assert isinstance(me, Me)
    assert me.username == "alice"
    assert me.identity.uid == "1"
    assert me.org.dir_id == "d1"


@responses.activate
@pytest.mark.integration
def test_cli_wiki_me_get(creds):
    responses.add(responses.GET, ME_URL, json=ME_BODY, status=200)
    res = CliRunner().invoke(cli.app, ["--format", "json", "wiki", "me", "get"])
    assert res.exit_code == 0
    assert "alice" in res.stdout


@responses.activate
@pytest.mark.integration
def test_mcp_wiki_me_get(creds):
    responses.add(responses.GET, ME_URL, json=ME_BODY, status=200)
    from ycli.yandex.wiki.me.mcp import get
    from ycli.yandex.wiki.client import WikiClient as WC
    result = get(client=WC.from_env())
    assert result.username == "alice"
```

Run: `uv run pytest tests/yandex/wiki/test_me.py -v`
Expected: FAIL (stubs don't parse `/users/me`).

- [ ] **Step 3: Fill `models.py`**

`src/ycli/yandex/wiki/me/models.py`:

```python
"""Pydantic models for Wiki /users/me (the authenticated user)."""
from __future__ import annotations

from pydantic import BaseModel


class Identity(BaseModel):
    uid: str | None = None
    cloud_uid: str | None = None


class Organization(BaseModel):
    dir_id: str | None = None
    collab_id: str | None = None


class Me(BaseModel):
    """The authenticated Wiki user (``GET /v1/users/me``) — a safe auth probe."""

    username: str | None = None
    home_cluster: str | None = None
    identity: Identity | None = None
    org: Organization | None = None
```

- [ ] **Step 4: Fill `client.py`**

`src/ycli/yandex/wiki/me/client.py` (no `from __future__ import annotations` — uplink reads annotations eagerly; no `@uplink.timeout` so the configurable adapter timeout applies):

```python
"""Declarative Wiki /users/me client (uplink) — transport ONLY."""
import uplink

from ycli.yandex.wiki._base import WikiResource
from ycli.yandex.wiki.me.models import Me


class MeClient(WikiResource):
    """Declarative HTTP for ``/users/me``."""

    @uplink.returns.json()
    @uplink.get("users/me")
    def get(self) -> Me:  # ty: ignore[empty-body]
        """``GET /users/me`` → the authenticated ``Me`` (a safe auth probe)."""
```

- [ ] **Step 5: Fill `cli.py`** (old `render(...)` signature — Task 6 threads the format)

`src/ycli/yandex/wiki/me/cli.py`:

```python
"""`wiki me` commands."""
from __future__ import annotations

import typer

from ycli.output import render
from ycli.yandex.wiki._clideps import wiki_client

app = typer.Typer(name="me", help="Wiki authenticated user.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context) -> None:
    """Print the authenticated user (a safe auth probe)."""
    render(wiki_client(ctx).me.get())
```

- [ ] **Step 6: Fill `mcp.py`**

`src/ycli/yandex/wiki/me/mcp.py`:

```python
"""Wiki /users/me FastMCP tool (read-only) — Depends DI."""
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.wiki._deps import RO, TAGS, wiki_client
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.me.models import Me

mcp = FastMCP("wiki-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Wiki user"}, tags=TAGS)
def get(client: WikiClient = Depends(wiki_client)) -> Me:
    """The authenticated Yandex Wiki user (a safe auth probe)."""
    result = client.me.get()
    if result.username is None:
        raise ValueError("auth probe failed — empty user (check YANDEX_ID_OAUTH_TOKEN)")
    return result
```

Set `src/ycli/yandex/wiki/me/__init__.py` to: `"""Yandex Wiki /users/me resource (the authenticated user)."""`

- [ ] **Step 7: Register in the three Wiki composition points (mount `me` first, mirroring tracker)**

- `wiki/client.py` `__init__`: add `self.me = MeClient(session=session)` as the first sub-client, and `from ycli.yandex.wiki.me.client import MeClient`.
- `wiki/cli.py`: add `from ycli.yandex.wiki.me.cli import app as me_app` and `app.add_typer(me_app)` as the first `add_typer`.
- `wiki/mcp.py`: add `from ycli.yandex.wiki.me.mcp import mcp as me_mcp` and `mcp.mount(me_mcp)` as the first mount.

- [ ] **Step 8: Run the resource tests**

Run: `uv run pytest tests/yandex/wiki/test_me.py -v`
Expected: PASS.

- [ ] **Step 9: Regenerate snapshots and verify the diff is exactly the additions**

Run: `uv run python -m tests.snapshots --update && git diff tests/snapshots/`
Expected: `cli_tree.txt` gains `wiki me` and `wiki me get`; `mcp_tools.txt` gains `wiki_me_get`. No other lines change.

- [ ] **Step 10: Full suite + lint + commit**

Run: `uv run pytest -q && uv run lint-imports`
Expected: all pass, 100% coverage, contracts 0 broken.

```bash
git add src/ycli/yandex/wiki/me tests/yandex/wiki/test_me.py \
        src/ycli/yandex/wiki/client.py src/ycli/yandex/wiki/cli.py src/ycli/yandex/wiki/mcp.py \
        tests/snapshots/cli_tree.txt tests/snapshots/mcp_tools.txt
git commit -m "feat: wiki me resource (GET /v1/users/me) completing four-surface me symmetry

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Move `auth` to `yandex/auth.py`, probe all three services

**Files:**
- Create: `src/ycli/yandex/auth.py`
- Delete: `src/ycli/authcli.py`
- Modify: `src/ycli/cli.py:12,39` (import `auth` app from new module)
- Test: delete `tests/test_auth_status.py`; create `tests/yandex/test_auth.py`

**Interfaces:**
- Consumes: `TrackerClient.me.get().login/.display`, `FormsClient.me.get().login/.display`, `WikiClient.me.get().username` (Task 3), `Credentials` (Task 1), `YandexAuthError`/`YandexError` (`yandex/errors.py`), `render` (`output.py`).
- Produces: a `auth` Typer app (`status` command); models `ServiceAuthStatus` and `AuthReport`.

- [ ] **Step 1: Write the failing tests**

Create `tests/yandex/test_auth.py`:

```python
"""`ycli auth status` — probes Tracker, Wiki, Forms identity endpoints."""
import pytest
import responses
from typer.testing import CliRunner

import ycli.cli as cli

TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"

runner = CliRunner()
pytestmark = pytest.mark.integration


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")


def test_missing_env_reports_not_configured(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    res = runner.invoke(cli.app, ["auth", "status"])
    assert res.exit_code == 1
    assert "YANDEX_ID_OAUTH_TOKEN" in res.stdout


@responses.activate
def test_all_services_valid(creds):
    responses.add(responses.GET, TRACKER_ME, json={"login": "alice", "display": "Alice"}, status=200)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 0
    assert res.stdout.count('"valid":true') == 3


@responses.activate
def test_one_service_invalid_sets_nonzero_exit(creds):
    responses.add(responses.GET, TRACKER_ME, status=401)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"email": "alice@x"}, status=200)
    res = runner.invoke(cli.app, ["--format", "json", "auth", "status"])
    assert res.exit_code == 1
    assert "tracker" in res.stdout
```

Run: `uv run pytest tests/yandex/test_auth.py -v`
Expected: FAIL (`auth` still resolves to the old `authcli` app / new module missing).

- [ ] **Step 2: Implement `src/ycli/yandex/auth.py`** (old `render(...)` signature — Task 6 threads format)

```python
"""`ycli auth status` — validate credentials against each service's identity endpoint.

Cross-cutting: sits above the three domains and imports their clients. CLI-only — the MCP
server stays read-only domain tools (no auth tool).
"""
from __future__ import annotations

import typer
from pydantic import BaseModel, ValidationError

from ycli.output import render
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.settings import Credentials
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)


class ServiceAuthStatus(BaseModel):
    """Per-service probe result. ``identity`` is the service's own user handle —
    Tracker ``login``, Wiki ``username``, Forms ``email``."""

    service: str
    valid: bool = False
    identity: str | None = None
    detail: str = ""


class AuthReport(BaseModel):
    """The full auth probe — rendered like any other ycli result."""

    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = []


def _probe_tracker() -> ServiceAuthStatus:
    try:
        me = TrackerClient.from_env().me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service="tracker", valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service="tracker", valid=False, detail=str(exc))
    return ServiceAuthStatus(service="tracker", valid=True, identity=me.login)


def _probe_forms() -> ServiceAuthStatus:
    try:
        me = FormsClient.from_env().me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service="forms", valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service="forms", valid=False, detail=str(exc))
    return ServiceAuthStatus(service="forms", valid=True, identity=me.email)


def _probe_wiki() -> ServiceAuthStatus:
    try:
        me = WikiClient.from_env().me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service="wiki", valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service="wiki", valid=False, detail=str(exc))
    return ServiceAuthStatus(service="wiki", valid=True, identity=me.username)


@app.command()
def status() -> None:
    """Report whether the env credentials are set and actually work, per service."""
    env_names = {
        "oauth_token": "YANDEX_ID_OAUTH_TOKEN",
        "organization_id": "YANDEX_ID_ORGANIZATION_ID",
    }
    try:
        credentials = Credentials()
    except ValidationError as exc:
        missing = ", ".join(
            env_names.get(str(error["loc"][0]), str(error["loc"][0])) for error in exc.errors()
        )
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        render(AuthReport(configured=False, services=[]))
        raise typer.Exit(1) from None

    services = [_probe_tracker(), _probe_wiki(), _probe_forms()]
    report = AuthReport(
        configured=True,
        organization_id=credentials.organization_id,
        services=services,
    )
    render(report)
    if not all(service.valid for service in services):
        raise typer.Exit(1)
```

The `env_names` map turns pydantic's field-name `loc` (`oauth_token`) into the published env-var name the test asserts on. typer's `CliRunner` mixes stderr into `res.stdout` by default, so the `err=True` line is visible to the assertion.

- [ ] **Step 3: Wire `cli.py` to the new module, delete `authcli.py`**

- In `src/ycli/cli.py` change `from ycli.authcli import app as auth_app` → `from ycli.yandex.auth import app as auth_app`.
- `rm src/ycli/authcli.py`
- `rm tests/test_auth_status.py`

- [ ] **Step 4: Run the auth tests, adjust the missing-var emission until green**

Run: `uv run pytest tests/yandex/test_auth.py -v`
Expected: PASS. If `test_missing_env_reports_not_configured` fails because the env-var name isn't in stdout, apply the field→alias mapping from Step 2's note.

- [ ] **Step 5: Full suite + lint (watch for cross-domain import contracts)**

Run: `uv run pytest -q && uv run lint-imports`
Expected: all pass, 100% coverage. `lint-imports` contracts 0 broken — `auth.py` imports all three domain clients (aggregator layer, like `cli.py`); if a contract forbids it, add `auth` to the same allowed aggregator layer as `cli` in `pyproject.toml`'s import-linter config and note it in the commit.

- [ ] **Step 6: Commit**

```bash
git add src/ycli/yandex/auth.py src/ycli/cli.py tests/yandex/test_auth.py
git rm src/ycli/authcli.py tests/test_auth_status.py
git commit -m "refactor: move auth to yandex/auth.py and probe Tracker/Wiki/Forms

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: `output.py` Strategy classes (internal refactor only)

**Files:**
- Modify: `src/ycli/output.py`
- Test: `tests/test_output_strategies.py` (new); existing `tests/test_output_links.py` must stay green unchanged

**Interfaces:**
- Consumes: nothing new.
- Produces: `SerializationStrategy` (ABC, `serialize(self, result: BaseModel, console: Console) -> None`), concrete `JsonStrategy`, `YamlStrategy`, `PrettyStrategy`, `AutoStrategy`. `render()` keeps its CURRENT public signature (`render(result, *, console=None)`) and the module global `_format` for now — only the internals change. (The global is removed in Task 6.)

- [ ] **Step 1: Write the failing strategy unit tests**

Create `tests/test_output_strategies.py`:

```python
"""output.py serialization strategies."""
from io import StringIO

from pydantic import BaseModel
from rich.console import Console

from ycli.output import AutoStrategy, JsonStrategy, PrettyStrategy, YamlStrategy


class _Row(BaseModel):
    key: str
    name: str


def _console(*, terminal: bool) -> tuple[Console, StringIO]:
    buf = StringIO()
    return Console(file=buf, force_terminal=terminal, width=200), buf


def test_json_strategy_emits_pristine_json_when_piped():
    console, buf = _console(terminal=False)
    JsonStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip() == '{"key":"ABC-1","name":"x"}'


def test_yaml_strategy_emits_yaml():
    console, buf = _console(terminal=False)
    YamlStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert "key: ABC-1" in buf.getvalue()


def test_pretty_strategy_links_key_on_terminal():
    console, buf = _console(terminal=True)
    PrettyStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert "tracker.yandex.ru/ABC-1" in buf.getvalue()


def test_auto_strategy_is_json_when_piped():
    console, buf = _console(terminal=False)
    AutoStrategy().serialize(_Row(key="ABC-1", name="x"), console)
    assert buf.getvalue().strip().startswith("{")
```

Run: `uv run pytest tests/test_output_strategies.py -v`
Expected: FAIL (`ImportError` — strategies not defined).

- [ ] **Step 2: Refactor `output.py` into strategies (behavior identical)**

Rewrite `src/ycli/output.py` keeping `OutputFormat`, the `_KEY_RE`/`_key_link` helpers, and `render`/`set_format`/`_format` as they are, but move the per-format bodies into strategy classes and the table helpers into `PrettyStrategy`:

```python
from abc import ABC, abstractmethod

class SerializationStrategy(ABC):
    @abstractmethod
    def serialize(self, result: BaseModel, console: Console) -> None: ...

class JsonStrategy(SerializationStrategy):
    def serialize(self, result: BaseModel, console: Console) -> None:
        text = result.model_dump_json(by_alias=True)
        if console.is_terminal:
            console.print_json(text)
        else:
            console.file.write(text + "\n")

class YamlStrategy(SerializationStrategy):
    def serialize(self, result: BaseModel, console: Console) -> None:
        data = result.model_dump(by_alias=True, mode="json")
        console.file.write(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))

class PrettyStrategy(SerializationStrategy):
    def serialize(self, result: BaseModel, console: Console) -> None:
        console.print(self._prettify(result.model_dump(by_alias=True, mode="json"), link=console.is_terminal))
    # move _prettify / _kv_table / _list_table / _cell here as methods (or keep as
    # module functions and call them) — keep the key-link logic unchanged.

class AutoStrategy(SerializationStrategy):
    def serialize(self, result: BaseModel, console: Console) -> None:
        strategy = PrettyStrategy() if console.is_terminal else JsonStrategy()
        strategy.serialize(result, console)

_STRATEGIES = {
    OutputFormat.json: JsonStrategy,
    OutputFormat.yaml: YamlStrategy,
    OutputFormat.pretty: PrettyStrategy,
    OutputFormat.auto: AutoStrategy,
}

def render(result: BaseModel, *, console: Console | None = None) -> None:
    console = console or Console()
    _STRATEGIES[_format]().serialize(result, console)
```

Keep `_prettify`/`_kv_table`/`_list_table`/`_cell` working (either as `PrettyStrategy` methods or retained module functions the strategy calls) — `tests/test_output_links.py` must pass unchanged.

- [ ] **Step 3: Run the strategy tests + the existing output tests**

Run: `uv run pytest tests/test_output_strategies.py tests/test_output_links.py -v`
Expected: PASS (both).

- [ ] **Step 4: Full suite + commit**

Run: `uv run pytest -q && uv run lint-imports`
Expected: all pass, 100% coverage.

```bash
git add src/ycli/output.py tests/test_output_strategies.py
git commit -m "refactor: output.py serialization strategy classes (behavior unchanged)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Remove the `output.py` global — thread format from the Context

**Files:**
- Create: `src/ycli/cliformat.py`
- Modify: `src/ycli/output.py` (drop `_format`/`set_format`, add `output_format` param), `src/ycli/cli.py` (drop `set_format` call/import), every CLI command that calls `render(...)` (list below), `src/ycli/yandex/auth.py`, `src/ycli/yandex/wiki/me/cli.py`
- Test: `tests/test_cliformat.py` (new); existing format/snapshot tests stay green

**Interfaces:**
- Consumes: `OutputFormat` (output.py), `Console`.
- Produces: `render(result, *, output_format: OutputFormat, console: Console | None = None)`; `cliformat.output_format(ctx: typer.Context) -> OutputFormat`. `_format`/`set_format` are gone.

**Render call sites to update (verified):**
```
src/ycli/yandex/wiki/comments/cli.py:22         src/ycli/yandex/tracker/comments/cli.py:20,30
src/ycli/yandex/wiki/pages/cli.py:38,51,66      src/ycli/yandex/tracker/linktypes/cli.py:21
src/ycli/yandex/wiki/attachments/cli.py:22      src/ycli/yandex/tracker/changelog/cli.py:27
src/ycli/yandex/wiki/me/cli.py (Task 3)         src/ycli/yandex/tracker/priorities/cli.py:21
src/ycli/yandex/tracker/transitions/cli.py:21   src/ycli/yandex/tracker/links/cli.py:33,45
src/ycli/yandex/tracker/issues/cli.py:25,51,57,104,134   src/ycli/yandex/tracker/worklog/cli.py:23
src/ycli/yandex/tracker/me/cli.py:20            src/ycli/yandex/forms/me/cli.py:21
src/ycli/yandex/tracker/issuetypes/cli.py:21    src/ycli/yandex/forms/questions/cli.py:27
src/ycli/yandex/forms/answers/cli.py:27         src/ycli/yandex/forms/surveys/cli.py:22,28
src/ycli/yandex/auth.py (Task 4)
```
Every one of these command bodies already has `ctx: typer.Context` in scope (they call `*_client(ctx)`); `auth.py status()` must add `ctx: typer.Context` as its first parameter.

- [ ] **Step 1: Write the failing helper test**

Create `tests/test_cliformat.py`:

```python
"""cliformat.output_format resolves the root --format option from any nested command."""
import typer
from typer.testing import CliRunner

from ycli.cliformat import output_format
from ycli.output import OutputFormat

app = typer.Typer()
sub = typer.Typer()
app.add_typer(sub, name="sub")


@app.callback()
def _root(fmt: OutputFormat = typer.Option(OutputFormat.auto, "--format")):
    pass


@sub.command()
def go(ctx: typer.Context):
    typer.echo(output_format(ctx).value)


def test_resolves_explicit_format():
    res = CliRunner().invoke(app, ["--format", "json", "sub", "go"])
    assert res.stdout.strip() == "json"


def test_defaults_to_auto():
    res = CliRunner().invoke(app, ["sub", "go"])
    assert res.stdout.strip() == "auto"
```

Run: `uv run pytest tests/test_cliformat.py -v`
Expected: FAIL (`ModuleNotFoundError: ycli.cliformat`).

- [ ] **Step 2: Implement `cliformat.py`**

```python
"""Resolve the root ``--format`` option from any (nested) command Context — DI, no global."""
from __future__ import annotations

import typer

from ycli.output import OutputFormat


def output_format(ctx: typer.Context) -> OutputFormat:
    """Return the ``--format`` chosen on the root app (defaults to ``auto``)."""
    chosen = ctx.find_root().params.get("output_format", OutputFormat.auto)
    return chosen if isinstance(chosen, OutputFormat) else OutputFormat(chosen)
```

Run: `uv run pytest tests/test_cliformat.py -v`
Expected: PASS.

- [ ] **Step 3: Change `render` to take `output_format`, drop the global**

In `src/ycli/output.py`: delete `_format` and `set_format`; change `render`:

```python
def render(result: BaseModel, *, output_format: OutputFormat, console: Console | None = None) -> None:
    console = console or Console()
    _STRATEGIES[output_format]().serialize(result, console)
```

- [ ] **Step 4: Update `cli.py` callback**

Remove `set_format` from the import (`from ycli.output import OutputFormat`) and delete the `set_format(output_format)` line. The callback still declares `output_format` (so it lands in `ctx.find_root().params`) and calls `configure(level=AppConfig().log_level)`. Keep the parameter name `output_format` (its option is `--format`).

- [ ] **Step 5: Thread the format through every render call site**

For each site in the list above, change `render(X)` → `render(X, output_format=output_format(ctx))`, adding `from ycli.cliformat import output_format` to the file. For `auth.py`, add `ctx: typer.Context` as the first param of `status()` and pass `output_format=output_format(ctx)` on its `render(...)` calls.

Mechanical, uniform; do them all, then rely on the existing CLI/format/snapshot tests to prove no output changed.

- [ ] **Step 6: Confirm no global remains**

Run: `rg -n "set_format|_format\b" src/ycli`
Expected: no hits except the `output_format` parameter/helper and `OutputFormat` enum.

- [ ] **Step 7: Full suite + lint**

Run: `uv run pytest -q && uv run lint-imports`
Expected: all pass, 100% coverage, contracts 0 broken. (Snapshot tests unchanged — output bytes are identical.)

- [ ] **Step 8: Commit**

```bash
git add src/ycli/cliformat.py src/ycli/output.py src/ycli/cli.py \
        src/ycli/yandex tests/test_cliformat.py
git commit -m "refactor: thread output format from the CLI context, drop the module global

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 7: Move the `mcp` launcher out of `cli.py`

**Files:**
- Create: `src/ycli/mcp_launcher.py`
- Modify: `src/ycli/cli.py:45-59` (register, don't define)
- Test: `tests/test_yandex_cli.py:30-36` (update the monkeypatch target)

**Interfaces:**
- Consumes: `ycli.mcp.main` (lazy import).
- Produces: `launch_mcp_server() -> None` in `ycli.mcp_launcher`, registered on the root app as the `mcp` command.

- [ ] **Step 1: Update the existing launcher test (red)**

In `tests/test_yandex_cli.py`, `test_mcp_subcommand_launches_server` currently monkeypatches `ycli.mcp.main`. Keep that target (the launcher still calls `ycli.mcp.main`), but if you move the lazy import, ensure the patch still intercepts. Add an assertion that the command is registered from the new module:

```python
def test_mcp_command_registered_from_launcher():
    from typer.main import get_command
    names = get_command(cli.app).commands  # click Group.commands maps name -> Command
    assert "mcp" in names
```

Run: `uv run pytest tests/test_yandex_cli.py::test_mcp_command_registered_from_launcher -v`
Expected: PASS already (command exists) — this pins behavior; the refactor must keep it green.

- [ ] **Step 2: Create `src/ycli/mcp_launcher.py`**

```python
"""The ``ycli mcp`` launcher — isolated so cli.py only mounts. Importable without the mcp extra."""
from __future__ import annotations

import typer


def launch_mcp_server() -> None:
    """Run the read-only MCP server over stdio (requires the ``mcp`` extra).

    Tools are namespaced ``wiki_*``, ``tracker_*``, ``forms_*``. Point an MCP client at
    ``ycli mcp``.
    """
    try:
        from ycli.mcp import main as run_server
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the 'mcp' extra
        raise typer.BadParameter(
            "The MCP server requires the 'mcp' extra. Install it with: "
            "uv add 'yandex-cli[mcp]'  (or: uv tool install 'yandex-cli[mcp]')."
        ) from exc
    run_server()
```

- [ ] **Step 3: Register (not define) in `cli.py`**

Remove the `@app.command(name="mcp") def mcp(): ...` block. After the `add_typer` calls, register the launcher:

```python
from ycli.mcp_launcher import launch_mcp_server
...
app.command(name="mcp")(launch_mcp_server)
```

`cli.py` is now: imports, root callback, four `add_typer`, one `app.command(...)` registration, and `main()`.

- [ ] **Step 4: Run the launcher tests**

Run: `uv run pytest tests/test_yandex_cli.py -v`
Expected: PASS (both the launch test and the registration test).

- [ ] **Step 5: Full suite + lint + commit**

Run: `uv run pytest -q && uv run lint-imports`
Expected: all pass, 100% coverage.

```bash
git add src/ycli/mcp_launcher.py src/ycli/cli.py tests/test_yandex_cli.py
git commit -m "refactor: extract the mcp launcher so cli.py only mounts

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Final verification (after Task 7)

- [ ] Run `uv run pytest -q` → 100% coverage, all green.
- [ ] Run `uv run lint-imports` → contracts 0 broken.
- [ ] Run `git diff main --stat` → only the intended files changed; snapshots show exactly `wiki me` / `wiki me get` / `wiki_me_get` additions.
- [ ] Grep clean: `rg -n "session_from_env|set_format|ORG_HEADER|authcli" src` → no hits.
- [ ] PR → review → merge as `feat:` → v0.6.0 → verify on PyPI → post-release `uv lock` + `build:` commit (memory `ycli-uvlock-drifts-after-each-release`).
