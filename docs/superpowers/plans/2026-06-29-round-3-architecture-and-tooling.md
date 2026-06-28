# Round-3 Architecture & Tooling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pay down round-2's duplication/altitude debt, add strict ruff+ty tooling, finish the CLI/MCP surface, close the ARCH-4/ARCH-5 enforcement gaps, and add agent-facing infra — without reorganizing the enforced four-surface tree.

**Architecture:** Surgical moves around the intact `yandex/<domain>/<resource>/{client,cli,mcp,models}.py` tree: two top-level files swap homes (`models.py`→`yandex/`, `settings.py`→top-level), `auth.py`→`status.py`, delete `mcp_launcher.py`, add `mcp_cli.py`. Shared construction hoists into `ClientFactory` + a cached MCP client factory; the round-2 strategy/serializer patterns become the bar for `PrettyStrategy` and pagination wrappers.

**Tech Stack:** Python ≥3.12 · uv · uplink+requests · pydantic v2 + pydantic-settings · typer · fastmcp 3.4.2 · rich · loguru · **new:** ruff, ty (dev) · graphify (external, `uv tool`).

**Spec:** [docs/superpowers/specs/2026-06-29-round-3-architecture-and-tooling-design.md](../specs/2026-06-29-round-3-architecture-and-tooling-design.md)

## Global Constraints

- **Auto-release on push to main** — Conventional-Commit prefixes; NEVER write a skip-ci token (`[skip ci]`/`[ci skip]`/`[no ci]`/`[skip actions]`/`[actions skip]`) or `skip-checks` trailer in any commit/squash message.
- **After a release:** `uv lock` + a `build:` commit (PSR bumps pyproject, not the lock).
- **100% coverage gate:** `uv run pytest` enforces `--cov-fail-under=100`. Every task stays green.
- **Dependencies via `uv add` / `uv add --dev`** — never hand-edit pyproject dependency arrays. `[tool.*]` config sections ARE hand-edited.
- **No hardcoded credentials**; env only at composition roots; pre-authenticated session injection stays rejected.
- **MCP stays read-only** (ARCH-3). No writes added this milestone.
- **Reproducible artifacts:** the README gif is regenerated from `docs/demo/demo.tape`, never hand-authored.
- **Full self-documenting names** — never abbreviate identifiers/env vars.
- **Changing an ARCH invariant** edits `ARCHITECTURE.md` AND its enforcing check in the SAME task, flagged in the commit body.
- Commits end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Branch → PR → explicit approval before merge.
- **Test commands:** `uv run pytest` (full), `uv run pytest <path> -v` (single), `uv run lint-imports` (import-linter), `uv run python -m tests.snapshots --update` (regenerate CLI/MCP snapshots — only on purpose, ARCH-6).

---

## Phase A — Strict tooling (ruff + ty)

> Lands FIRST. Staged into four commits so the mechanical formatter diff is isolated from the semantic lint/annotation diffs. ty is advisory (beta).

### Task A1: Ruff formatter (mechanical, isolated)

**Files:**
- Modify: `pyproject.toml` (add `[tool.ruff]`, `[tool.ruff.format]`), `uv.lock`
- Modify: `.pre-commit-config.yaml`, `.github/workflows/ci.yml`
- Reformat: all of `src/`, `tests/`, `scripts/`

**Interfaces:**
- Produces: a repo where `uv run ruff format --check .` is clean. Later tasks assume formatted code.

- [ ] **Step 1: Install ruff as a dev dependency**

Run: `uv add --dev ruff`
Expected: ruff added to `[dependency-groups].dev`, `uv.lock` updated.

- [ ] **Step 2: Add formatter config to `pyproject.toml`**

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src", "tests", "scripts"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
skip-magic-trailing-comma = false
docstring-code-format = true
```

- [ ] **Step 3: Apply the formatter**

Run: `uv run ruff format .`
Expected: a large, mechanical diff. Inspect that `scripts/new_endpoint.py` template *string literals* (the `MODELS`/`CLIENT`/… constants) are untouched — only true docstrings get `docstring-code-format`.

- [ ] **Step 4: Verify the suite still passes after reformat**

Run: `uv run pytest`
Expected: 246 passed, 100% coverage (formatting changes no behavior).

- [ ] **Step 5: Wire pre-commit + CI**

Add to `.pre-commit-config.yaml` (before the `architecture-tests` hook), pinning `rev` to the installed ruff version:
```yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.0  # set to the exact version `uv run ruff version` prints
    hooks:
      - id: ruff-format
```
Add to `.github/workflows/ci.yml` `test` job (single interpreter is enough, but keeping it in the matrix step is fine):
```yaml
      - name: Format check
        run: uv run ruff format --check .
```

- [ ] **Step 6: Verify pre-commit + lock**

Run: `uv run pre-commit run ruff-format --all-files` then `uv lock`
Expected: hook passes; lock in sync.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "style: adopt ruff formatter (mechanical reformat, no behavior change)"
```

### Task A2: Ruff linter — conservative autofix select

**Files:**
- Modify: `pyproject.toml` (`[tool.ruff.lint]`, `[tool.ruff.lint.isort]`, `[tool.ruff.lint.per-file-ignores]`)
- Modify: `.pre-commit-config.yaml`, `.github/workflows/ci.yml`
- Fix: lint findings across `src/`, `tests/`, `scripts/`

**Interfaces:**
- Consumes: A1's formatted tree.
- Produces: `uv run ruff check .` clean. `I` (isort) now governs import order.

- [ ] **Step 1: Add lint config (autofix-heavy families first; ANN/TC deferred to A3)**

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "PTH", "RUF"]
ignore = ["ANN401"]

[tool.ruff.lint.isort]
known-first-party = ["ycli"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["N802"]
"scripts/**/*.py" = ["T201"]
```

- [ ] **Step 2: Autofix what ruff can**

Run: `uv run ruff check --fix .`
Expected: imports re-sorted, comprehensions/bugbear/pyupgrade fixes applied.

- [ ] **Step 3: Resolve residual findings by hand**

Run: `uv run ruff check .`
Expected: remaining findings printed. Fix each (do NOT blanket-ignore a family to silence one finding — use a targeted `# noqa: CODE` only with a reason, or fix the code). Re-run until clean.

- [ ] **Step 4: Verify suite + import-linter**

Run: `uv run pytest && uv run lint-imports`
Expected: 246 passed, 100% coverage; import-linter 2 kept / 0 broken.

- [ ] **Step 5: Wire the lint hook + CI**

Add the `ruff` hook (with `--fix`) above `ruff-format` in `.pre-commit-config.yaml`:
```yaml
      - id: ruff
        args: [--fix]
```
Add to CI:
```yaml
      - name: Lint
        run: uv run ruff check .
```

- [ ] **Step 6: Commit**

```bash
git add -A && uv lock && git add uv.lock
git commit -m "style: enable ruff lint (E,W,F,I,N,UP,B,A,C4,SIM,PTH,RUF) with autofix"
```

### Task A3: Ruff annotations + type-checking-imports ratchet

**Files:**
- Modify: `pyproject.toml` (`select` += `ANN`, `TC`; client.py ANN carve-out)
- Fix: missing annotations / type-only imports across `src/`

**Interfaces:**
- Consumes: A2's clean tree. Produces: a fully `ANN`-annotated public surface.

- [ ] **Step 1: Extend select + carve out the uplink stubs**

```toml
# [tool.ruff.lint]
select = ["E","W","F","I","N","UP","B","A","C4","SIM","PTH","RUF","ANN","TC"]

# [tool.ruff.lint.per-file-ignores]  (add)
"tests/**/*.py" = ["N802", "ANN"]
"scripts/**/*.py" = ["T201", "ANN"]
"src/ycli/yandex/**/client.py" = ["ANN"]   # uplink empty-body stubs read annotations eagerly
```

- [ ] **Step 2: Run, then hand-add annotations**

Run: `uv run ruff check .`
Expected: `ANN`/`TC` findings outside the carve-outs. Add the missing return/param annotations; move type-only imports under `if TYPE_CHECKING:` where `TC` asks. Re-run until clean.

- [ ] **Step 3: Verify**

Run: `uv run pytest && uv run lint-imports`
Expected: green, 100% coverage, import-linter intact.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "style: ratchet ruff ANN+TC (annotations + type-checking imports)"
```

### Task A4: ty type checker (advisory)

**Files:**
- Modify: `pyproject.toml` (`[tool.ty.*]`), `uv.lock`
- Modify: `.pre-commit-config.yaml`, `.github/workflows/ci.yml`
- Possibly: stale `# ty: ignore` cleanups across `src/ycli/yandex/**/client.py`

**Interfaces:**
- Produces: `uv run ty check` runnable; CI runs it advisory (`continue-on-error`).

- [ ] **Step 1: Install ty (pinned)**

Run: `uv add --dev ty`
Expected: ty in dev deps; note the exact version for hook pinning.

- [ ] **Step 2: Add ty config**

```toml
[tool.ty.environment]
python-version = "3.12"

[tool.ty.terminal]
error-on-warning = true

[tool.ty.rules]
possibly-unresolved-reference = "error"
unused-ignore-comment = "warn"
```

- [ ] **Step 3: Run ty, fix or re-suppress**

Run: `uv run ty check`
Expected: findings. For each: fix the type, or (for the documented uplink empty-body pattern) keep/repair the `# ty: ignore[<code>]`. Resolve every `unused-ignore-comment` warning (delete stale suppressions). Do NOT broaden ignores to silence real findings.

- [ ] **Step 4: Wire advisory hook + CI**

`.pre-commit-config.yaml`:
```yaml
  - repo: https://github.com/astral-sh/ty-pre-commit
    rev: 0.0.0  # exact installed ty version
    hooks:
      - id: ty
```
`.github/workflows/ci.yml` (advisory while ty is beta):
```yaml
      - name: Type check (advisory)
        run: uv run ty check
        continue-on-error: true
```

- [ ] **Step 5: Verify + lock**

Run: `uv run pytest && uv lock`
Expected: green; lock synced.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "build: add ty type checker (advisory CI gate while ty is beta)"
```

---

## Phase B — Composition & DI

### Task B1: Move `APIModel` → `ycli/yandex/models.py`

**Files:**
- Move: `src/ycli/models.py` → `src/ycli/yandex/models.py`
- Modify: every importer (`from ycli.models import APIModel` → `from ycli.yandex.models import APIModel`)
- Modify: `scripts/new_endpoint.py` (MODELS template), `ARCHITECTURE.md` (Layout lines 12, 21, 26), `tests/test_models.py` import

**Interfaces:**
- Produces: `ycli.yandex.models.APIModel` (same `ConfigDict(extra="ignore", populate_by_name=True)`).

- [ ] **Step 1: Move the file and rewrite imports**

```bash
git mv src/ycli/models.py src/ycli/yandex/models.py
grep -rl 'from ycli.models import APIModel' src tests | xargs sed -i 's#from ycli.models import APIModel#from ycli.yandex.models import APIModel#'
```
Also update the `scripts/new_endpoint.py` `MODELS` template string (`from ycli.models import APIModel` → `from ycli.yandex.models import APIModel`) and `ARCHITECTURE.md` Layout/notes mentioning `src/ycli/models.py`.

- [ ] **Step 2: Verify no stale references remain**

Run: `grep -rn 'ycli.models' src tests scripts ARCHITECTURE.md`
Expected: no hits (only `ycli.yandex.models`).

- [ ] **Step 3: Verify suite + imports + format/lint**

Run: `uv run pytest && uv run lint-imports && uv run ruff check . && uv run ruff format --check .`
Expected: green; import-linter intact (the base is `ycli.yandex.models`, outside the `yandex.**.models` glob).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: move APIModel base into ycli.yandex.models (thin top-level)"
```

### Task B2: Hoist settings → top-level `ycli/settings.py`

**Files:**
- Move: `src/ycli/yandex/settings.py` → `src/ycli/settings.py`
- Modify: every importer (`from ycli.yandex.settings import …` → `from ycli.settings import …`)
- Modify: `tests/test_architecture.py` ARCH-8 path (`settings = YANDEX / "settings.py"` → `settings = SRC / "settings.py"`)
- Modify: `ARCHITECTURE.md` (ARCH-5/ARCH-8 wording + Layout)

**Interfaces:**
- Produces: `ycli.settings.AppConfig`, `ycli.settings.Credentials` (unchanged fields).

- [ ] **Step 1: Move + rewrite imports**

```bash
git mv src/ycli/yandex/settings.py src/ycli/settings.py
grep -rl 'ycli.yandex.settings' src tests scripts | xargs sed -i 's#ycli.yandex.settings#ycli.settings#g'
```
Update `scripts/new_endpoint.py` if it references the settings path.

- [ ] **Step 2: Update the ARCH-8 check path**

In `tests/test_architecture.py`, the `test_arch8_*` test pins `settings = YANDEX / "settings.py"`. Change to the top-level path. Confirm `SRC` is defined in that file (it is — used by other checks); if the test computes `YANDEX = SRC / "yandex"`, use `SRC / "settings.py"`.

- [ ] **Step 3: Update ARCHITECTURE.md (same-task invariant change)**

ARCH-8 prose ("…outside `src/ycli/yandex/settings.py`") → "…outside `src/ycli/settings.py`". Update ARCH-5's mention if it names the settings path, and the Layout block.

- [ ] **Step 4: Verify**

Run: `grep -rn 'yandex.settings' src tests scripts && uv run pytest && uv run lint-imports`
Expected: no stale path hits; green; ARCH-8 test exercises the new path.

- [ ] **Step 5: Commit (flag the invariant edit)**

```bash
git add -A
git commit -m "refactor: hoist settings to top-level ycli.settings; update ARCH-8 path

ARCH-8 enforcing check + ARCHITECTURE.md edited together (settings path move)."
```

### Task B3: `ClientFactory` + cached MCP factory; collapse `_deps.py`; slim `AppContext`

**Files:**
- Create: `src/ycli/yandex/factory.py`
- Modify: `src/ycli/yandex/_mcp.py` (add `app_config()` + `make_cached_client()`)
- Rewrite: `src/ycli/yandex/{tracker,wiki,forms}/_deps.py` (thin)
- Modify: `src/ycli/context.py` (use `ClientFactory`, add `config` property)
- Modify: `tests/conftest.py` (cache_clear for `app_config` + each `<domain>_client`)
- Test: `tests/yandex/test_factory.py` (new), existing `tests/test_context.py`, `_deps` tests

**Interfaces:**
- Produces:
  - `ClientFactory.build(client_cls: type, credentials: Credentials, config: AppConfig) -> object` — env-free; maps creds+config to the raw client kwargs.
  - `ycli.yandex._mcp.app_config() -> AppConfig` — `@cache`d.
  - `ycli.yandex._mcp.make_cached_client(client_cls: type)` -> a `@cache`d zero-arg provider returning a built client.
  - `AppContext.config -> AppConfig` (lazy public property).
  - Each `_deps.py` exposes module-level `<domain>_client` (a cached provider) + `TAGS` + re-exported `RO`.
- Consumes: B1 (`ycli.yandex.models`), B2 (`ycli.settings`).

- [ ] **Step 1: Write the failing factory test**

`tests/yandex/test_factory.py`:
```python
from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import ClientFactory
from ycli.yandex.tracker.client import TrackerClient


def test_build_passes_raw_args_and_does_not_read_env():
    creds = Credentials(oauth_token="t", organization_id="o")
    cfg = AppConfig(timeout_seconds=12.0, retries=5)
    client = ClientFactory.build(TrackerClient, creds, cfg)
    assert isinstance(client, TrackerClient)
    assert client.session.headers["Authorization"] == "OAuth t"
    assert client.session.headers["X-Org-Id"] == "o"
```
(Confirm the client exposes `.session`; clients subclass the domain `_base` `Resource` which subclasses uplink `Consumer` with the session — adjust the attribute to the real one if needed by reading `yandex/<domain>/_base.py`.)

- [ ] **Step 2: Run it (fails — module missing)**

Run: `uv run pytest tests/yandex/test_factory.py -v`
Expected: FAIL (`ModuleNotFoundError: ycli.yandex.factory`).

- [ ] **Step 3: Implement `ClientFactory`**

`src/ycli/yandex/factory.py`:
```python
"""The single client-construction site — maps app config + credentials to raw client args.

Env-free by design (ARCH-7/8): callers at the composition roots (AppContext, the MCP
``_deps`` providers) read the environment and hand instances here.
"""
from __future__ import annotations

from ycli.settings import AppConfig, Credentials


class ClientFactory:
    """Builds a domain client from credentials + app config — no environment access."""

    @staticmethod
    def build(client_cls: type, credentials: Credentials, config: AppConfig) -> object:
        return client_cls(
            oauth_token=credentials.oauth_token,
            organization_id=credentials.organization_id,
            timeout_seconds=int(config.timeout_seconds),
            retries=config.retries,
        )
```

- [ ] **Step 4: Add the cached MCP factory to `_mcp.py`**

`src/ycli/yandex/_mcp.py`:
```python
"""Shared FastMCP tool annotations + the cached per-domain client/config providers."""
from __future__ import annotations

from functools import cache

from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import ClientFactory

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}


@cache
def app_config() -> AppConfig:
    """Build (once) the process-wide app config for MCP tools."""
    return AppConfig()


def make_cached_client(client_cls: type):
    """Return a ``@cache``d zero-arg provider building ``client_cls`` from the env."""

    @cache
    def provider() -> object:
        return ClientFactory.build(client_cls, Credentials(), app_config())

    return provider
```

- [ ] **Step 5: Collapse each `_deps.py`**

`src/ycli/yandex/tracker/_deps.py` (wiki/forms identical but for the client + TAGS):
```python
"""Cached tracker MCP client provider (see ycli.yandex._mcp.make_cached_client)."""
from ycli.yandex._mcp import RO, app_config, make_cached_client
from ycli.yandex.tracker.client import TrackerClient

TAGS: set[str] = {"tracker"}
tracker_client = make_cached_client(TrackerClient)

__all__ = ["RO", "TAGS", "app_config", "tracker_client"]
```

- [ ] **Step 6: Slim `AppContext`**

`src/ycli/context.py` — replace `_client` body + add `config`:
```python
    @property
    def config(self) -> AppConfig:
        if self._config is None:
            self._config = AppConfig()
        return self._config

    def _client(self, name: str, client_cls: type) -> object:
        if name not in self._clients:
            self._credentials = self._credentials or Credentials()
            self._clients[name] = ClientFactory.build(client_cls, self._credentials, self.config)
        return self._clients[name]
```
Update imports: `from ycli.settings import AppConfig, Credentials`, `from ycli.yandex.factory import ClientFactory`. Keep the lazy `tracker`/`wiki`/`forms` properties.

- [ ] **Step 7: Update conftest cache resets**

`tests/conftest.py` autouse fixture must clear the new caches:
```python
    from ycli.yandex import _mcp
    from ycli.yandex.tracker import _deps as tracker_deps
    from ycli.yandex.wiki import _deps as wiki_deps
    from ycli.yandex.forms import _deps as forms_deps
    _mcp.app_config.cache_clear()
    tracker_deps.tracker_client.cache_clear()
    wiki_deps.wiki_client.cache_clear()
    forms_deps.forms_client.cache_clear()
```
(Adapt to the fixture's existing structure.)

- [ ] **Step 8: Run factory test + full suite + imports**

Run: `uv run pytest tests/yandex/test_factory.py -v && uv run pytest && uv run lint-imports && uv run ruff check .`
Expected: factory test passes; 100% coverage; import-linter intact. The 4× construction duplication is gone.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "refactor(di): ClientFactory + cached MCP factory; collapse _deps; slim AppContext"
```

### Task B4: Config-injection rule (Depends(app_config) / AppContext.config)

**Files:**
- Modify: `src/ycli/yandex/forms/answers/mcp.py`, `src/ycli/yandex/wiki/pages/mcp.py` (use `Depends(app_config)`)
- Modify: `src/ycli/yandex/forms/answers/cli.py`, `src/ycli/yandex/wiki/pages/cli.py` (use `app_ctx.config.max_items`)
- Test: the existing mcp/cli tests for those resources

**Interfaces:**
- Consumes: `app_config` (B3), `AppContext.config` (B3).
- Produces: no on-the-fly `AppConfig()` in any tool/command body (except `log_level` at the two `main()` roots).

- [ ] **Step 1: Inject config into the MCP tools**

In `forms/answers/mcp.py`, change the body from `AppConfig().max_items` to an injected param. Example shape:
```python
from fastmcp.dependencies import Depends
from ycli.yandex.forms._deps import RO, TAGS, app_config, forms_client
from ycli.settings import AppConfig

@mcp.tool(name="answers_list", annotations={**RO, "title": "List Forms answers"}, tags=TAGS)
def list(survey_id: str, client: FormsClient = Depends(forms_client),
         cfg: AppConfig = Depends(app_config)) -> AnswersResponse:
    """List all answers for a survey (auto-paginated, bounded by YCLI_MAX_ITEMS)."""
    return client.answers.list_all(survey_id, limit=cfg.max_items)
```
Re-export `app_config` from each `_deps.py` (done in B3 `__all__`). Do the same for `wiki/pages/mcp.py` (`cap = limit or cfg.max_items`).

- [ ] **Step 2: Read config off AppContext in the CLI**

In `forms/answers/cli.py` and `wiki/pages/cli.py`, replace `AppConfig()` with `app_ctx.config`:
```python
cap = None if all_ else (limit or app_ctx.config.max_items)
```
Drop the now-unused `from ycli.settings import AppConfig` import from those CLI modules.

- [ ] **Step 3: Verify `AppConfig()` no longer appears in leaf bodies**

Run: `grep -rn 'AppConfig()' src/ycli/yandex`
Expected: no hits (the only allowed bare reads are `AppConfig().log_level` in `src/ycli/cli.py` and `src/ycli/mcp.py`). `_mcp.app_config()` wraps the MCP read.

- [ ] **Step 4: Run the affected tests + full suite**

Run: `uv run pytest tests/yandex/forms/answers tests/yandex/wiki/pages -v && uv run pytest`
Expected: green; 100% coverage. The `Depends`-injected `cfg` is hidden from the tool schema (no snapshot change).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(di): inject AppConfig via Depends(app_config)/AppContext.config; no on-the-fly settings"
```

---

## Phase C — Transport / status / auth

### Task C1: `_raise_typed` → `@staticmethod` on `Transport`; auth-scheme seam

**Files:**
- Modify: `src/ycli/yandex/transport.py`
- Modify: `tests/yandex/test_transport.py` (import `Transport`, assert `Transport._raise_typed`)

**Interfaces:**
- Produces: `Transport._raise_typed` (staticmethod, same signature/behavior); `Transport._authorization(oauth_token) -> str` (private header-build seam).

- [ ] **Step 1: Update the failing test**

In `tests/yandex/test_transport.py`, the hook-membership test imports `_raise_typed` directly. Change to:
```python
from ycli.yandex.transport import Transport
...
def test_response_hook_is_registered():
    s = Transport.session(oauth_token="t", organization_id="o")
    assert Transport._raise_typed in s.hooks["response"]
```
Add a seam test:
```python
def test_authorization_header_uses_oauth_scheme():
    assert Transport._authorization("abc") == "OAuth abc"
```

- [ ] **Step 2: Run (fails)**

Run: `uv run pytest tests/yandex/test_transport.py -v`
Expected: FAIL (`_raise_typed` no longer importable as module-level once moved / `_authorization` missing).

- [ ] **Step 3: Move `_raise_typed` into `Transport` + add the seam**

In `transport.py`: indent `_raise_typed` into `Transport` as `@staticmethod` (drop the leading `_raise_typed` module function). Add the header seam and use both:
```python
class Transport:
    @staticmethod
    def _authorization(oauth_token: str) -> str:
        """The Authorization header value — the single point an auth scheme would vary."""
        return f"OAuth {oauth_token}"

    @staticmethod
    def _raise_typed(response: Response, *args: Any, **kwargs: Any) -> Response:
        ...  # unchanged body

    @classmethod
    def session(cls, *, oauth_token, organization_id, timeout_seconds=30.0, retries=3, base=None):
        ...
        session.headers.update(
            {"Authorization": cls._authorization(oauth_token), "X-Org-Id": organization_id}
        )
        session.hooks["response"].append(cls._raise_typed)
        ...
```
Keep `_TimeoutAdapter` as-is (module-level is fine — it's a class, not the hook).

- [ ] **Step 4: Run transport test + full suite + ARCH**

Run: `uv run pytest tests/yandex/test_transport.py -v && uv run pytest && uv run pytest tests/test_architecture.py -v`
Expected: green; ARCH-9 still satisfied (typed-error mapping stays in transport.py).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(transport): _raise_typed as Transport staticmethod; extract _authorization seam"
```

### Task C2: Rename `auth.py` → `status.py`; `ServiceProbe` class

**Files:**
- Move: `src/ycli/yandex/auth.py` → `src/ycli/yandex/status.py`
- Modify: `src/ycli/cli.py` (import path)
- Modify: the status test module import (`tests/yandex/test_auth*.py` → adjust import; optionally rename file)

**Interfaces:**
- Consumes: `ClientFactory`/`Credentials` (B), `Serializer`, `APIModel` (`ycli.yandex.models`).
- Produces: Typer app still `name="auth"`, command `status` — `ycli auth status` UNCHANGED (no snapshot change). `ServiceProbe` class replaces `_PROBES`/`_probe`.

- [ ] **Step 1: Move the file, keep the command name**

```bash
git mv src/ycli/yandex/auth.py src/ycli/yandex/status.py
sed -i 's#from ycli.yandex.auth import app as auth_app#from ycli.yandex.status import app as auth_app#' src/ycli/cli.py
```
Keep `app = typer.Typer(name="auth", ...)` and `@app.command() def status(...)` so the CLI tree is identical.

- [ ] **Step 2: Replace `_PROBES`/`_probe` with `ServiceProbe`**

In `status.py`:
```python
class ServiceProbe:
    """One service's identity check — keeps its name, client class, and identity extractor together."""

    def __init__(self, name: str, client_cls: type, identity_of: Callable[[object], str]) -> None:
        self._name, self._client_cls, self._identity_of = name, client_cls, identity_of

    def run(self, credentials: Credentials) -> ServiceAuthStatus:
        client = ClientFactory.build(self._client_cls, credentials, AppConfig())
        try:
            me = client.me.get()
        except YandexAuthError:
            return ServiceAuthStatus(service=self._name, valid=False, detail="token invalid or expired")
        except YandexError as exc:
            return ServiceAuthStatus(service=self._name, valid=False, detail=str(exc))
        return ServiceAuthStatus(service=self._name, valid=True, identity=self._identity_of(me))


PROBES: list[ServiceProbe] = [
    ServiceProbe("tracker", TrackerClient, lambda me: me.login),
    ServiceProbe("wiki", WikiClient, lambda me: me.username),
    ServiceProbe("forms", FormsClient, lambda me: me.email),
]
```
In `status()`, replace the comprehension: `services = [p.run(credentials) for p in PROBES]`. Update imports (`from ycli.yandex.factory import ClientFactory`, `from ycli.settings import AppConfig, Credentials`, `from ycli.yandex.models import APIModel`).

- [ ] **Step 3: Fix the test import**

The status test imports from `ycli.yandex.auth`. Update to `ycli.yandex.status` (and optionally `git mv` the test file to `test_status.py`). The identity extractors still need their per-service branch covered — keep the existing tests that exercise tracker/wiki/forms identity + the auth-failure + not-configured paths.

- [ ] **Step 4: Verify suite + snapshot unchanged**

Run: `uv run pytest && uv run pytest tests/test_snapshots.py -v`
Expected: green; CLI snapshot UNCHANGED (`auth status` preserved).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: rename auth.py->status.py (keep 'auth status'); fold probes into ServiceProbe"
```

---

## Phase D — Dedup, conventions & the ARCH-4 gap

### Task D1: Close the ARCH-4 `json.dumps` hole

**Files:**
- Create: `RawMapping` RootModel in `src/ycli/yandex/models.py`
- Modify: `src/ycli/yandex/tracker/issues/cli.py` (`full` renders via Serializer)
- Modify: `tests/test_architecture.py` (ARCH-4: forbid `json.dumps` outside `output.py`), `ARCHITECTURE.md` (ARCH-4 wording)
- Test: `tests/yandex/tracker/issues/test_cli.py` (`full` now honors `--format`)

**Interfaces:**
- Produces: `ycli.yandex.models.RawMapping` (`RootModel[dict[str, Any]]`).

- [ ] **Step 1: Tighten the ARCH-4 check (failing first)**

In `tests/test_architecture.py`, the ARCH-4 test greps for `model_dump_json`/`yaml.safe_dump` outside `output.py`. Add `json.dumps` to that forbidden set (scanning `SRC`, excluding `output.py`).

Run: `uv run pytest tests/test_architecture.py -k arch4 -v`
Expected: FAIL — it now flags `tracker/issues/cli.py` (and `tracker/transitions/cli.py`, handled in D2).

- [ ] **Step 2: Add the `RawMapping` model**

In `src/ycli/yandex/models.py`:
```python
from typing import Any
from pydantic import RootModel

class RawMapping(RootModel[dict[str, Any]]):
    """Wraps an unmodeled API dict so it renders through the Serializer (honoring --format)."""
```

- [ ] **Step 3: Route `issues full` through the Serializer**

In `tracker/issues/cli.py`, replace `print(json.dumps(app_ctx.tracker.issues.get_raw(key), ensure_ascii=False))` with:
```python
from ycli.yandex.models import RawMapping
...
Serializer.serialize(RawMapping(app_ctx.tracker.issues.get_raw(key)), app_ctx.strategy, app_ctx.console)
```
Keep `get_raw` returning a raw `dict` (the unpruned escape hatch is intentional).

- [ ] **Step 4: Update ARCHITECTURE.md (same-task invariant change)**

ARCH-4 *Check* line: add `json.dumps` to the confined set. Note the carve-out: a bare `print(int)` for scalar `count` is fine (not model output).

- [ ] **Step 5: Update the test + verify**

Update `test_full_*` in the issues CLI test to assert the value renders via the chosen format (e.g. with `-o json` the dict appears; default pretty renders a table). Run:
`uv run pytest tests/yandex/tracker/issues -v && uv run pytest tests/test_architecture.py -k arch4 -v && uv run pytest`
Expected: green, 100% coverage.

- [ ] **Step 6: Commit (flag invariant edit)**

```bash
git add -A
git commit -m "fix(arch-4): route issues full through Serializer; forbid json.dumps outside output.py

ARCH-4 check + ARCHITECTURE.md tightened together (json.dumps blind spot)."
```

### Task D2: Model `transitions execute`

**Files:**
- Read first: `src/ycli/yandex/tracker/transitions/{client,models}.py`, `src/ycli/yandex/tracker/transitions/cli.py`, `docs/references/yandex/tracker/` (transition response shape)
- Modify: those three files
- Test: `tests/yandex/tracker/transitions/*`

**Interfaces:**
- Produces: `TransitionsClient.execute(...) -> TransitionList` (a `RootModel[list[Transition]]`), removing the `builtins.list` shadow hack.

- [ ] **Step 1: Read the current shape**

Read the transitions client/models and a sample response in `docs/references/yandex/tracker/`. Confirm the post-execute payload is a list of transition objects matching the existing `Transition` model (fields like `id`, `display`, `to`). If the shape differs, define a dedicated model rather than forcing a lossy fit.

- [ ] **Step 2: Define/confirm `TransitionList`**

If not present, in `transitions/models.py`:
```python
from pydantic import RootModel
class TransitionList(RootModel[list[Transition]]):
    """A flat list of issue transitions."""
```

- [ ] **Step 3: Change `execute` return type**

In `transitions/client.py`, change `execute`'s annotation from `builtins.list` to `TransitionList` (this also removes the `# ty: ignore`/shadowing workaround). Keep the uplink decorators; do NOT add `from __future__ import annotations`.

- [ ] **Step 4: Render via Serializer in the CLI**

In `transitions/cli.py`, replace `print(json.dumps(raw, ...))` with `Serializer.serialize(<result>, app_ctx.strategy, app_ctx.console)`.

- [ ] **Step 5: Verify (incl. ARCH-4 now fully clean)**

Run: `uv run pytest tests/yandex/tracker/transitions -v && uv run pytest tests/test_architecture.py -k arch4 -v && uv run pytest`
Expected: green; ARCH-4 passes (last `json.dumps` removed). Note in the commit: SDK return type changed (public-surface change for SDK consumers; ARCH-6 locks names, not signatures).

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(tracker): model transitions execute as TransitionList; render via Serializer"
```

### Task D3: Collapse the single-page `list` wrappers

**Files:**
- Read first: `src/ycli/yandex/wiki/attachments/client.py`, `src/ycli/yandex/wiki/comments/client.py`, `src/ycli/yandex/forms/surveys/client.py`, `src/ycli/yandex/pagination.py`
- Create: a shared helper (in `src/ycli/yandex/pagination.py` or `base.py`)
- Modify: the three clients
- Test: the three resources' client tests + a direct helper test

**Interfaces:**
- Produces: a shared single-page collect helper, e.g. `collect_single_page(page_fn, *, extract, wrap, limit)` returning `wrap(items)`.

- [ ] **Step 1: Read the three wrappers + pagination strategies**

Confirm the shared shape: a private `_list_page` uplink method + a public `list(self, *, limit=None)` that runs `SinglePageStrategy(extract=lambda page: page.results).collect(lambda cursor: self._list_page(...), limit)` and wraps in a `RootModel`. Note the deltas: extract attr (`.results` vs `.result`), the wrap type, page args.

- [ ] **Step 2: Write the failing helper test**

`tests/yandex/test_pagination.py` (add):
```python
from ycli.yandex.pagination import collect_single_page

def test_collect_single_page_extracts_wraps_and_bounds():
    pages = {"a": [1, 2, 3]}
    out = collect_single_page(lambda cursor: pages, extract=lambda p: p["a"], wrap=list, limit=2)
    assert out == [1, 2]
```

- [ ] **Step 3: Run (fails)**

Run: `uv run pytest tests/yandex/test_pagination.py -k single_page -v`
Expected: FAIL (function missing).

- [ ] **Step 4: Implement the helper**

In `pagination.py`:
```python
def collect_single_page(page_fn, *, extract, wrap, limit=None):
    """Single-page envelope → bounded, wrapped flat collection (the wiki/forms list shape)."""
    items = SinglePageStrategy(extract=extract).collect(page_fn, limit)
    return wrap(items)
```
(Match the real `SinglePageStrategy.collect` signature from `pagination.py`.)

- [ ] **Step 5: Rewrite the three clients' public `list` to call the helper**

Keep each `_list_page` uplink method (HTTP stays per-client — ARCH-1/uplink). Public `list` becomes a thin call to `collect_single_page(...)` with the resource's `extract`/`wrap`.

- [ ] **Step 6: Verify**

Run: `uv run pytest tests/yandex/wiki/attachments tests/yandex/wiki/comments tests/yandex/forms/surveys tests/yandex/test_pagination.py -v && uv run pytest`
Expected: green; 100% coverage; ~36 lines of triplication gone.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor(pagination): hoist single-page list wrapper into collect_single_page helper"
```

### Task D4: Convention cleanups + resources doc

**Files:**
- Modify: `src/ycli/yandex/tracker/me/models.py`, `src/ycli/yandex/wiki/me/models.py` (inherit `APIModel`)
- Delete: `src/ycli/yandex/forms/_models.py` (dead tombstone)
- Modify: `src/ycli/yandex/forms/surveys/models.py` (rename `SurveyList`↔`SurveyCollection` to the `XList = flat RootModel` convention)
- Reconcile: the `RO` import path (scaffold `from ycli.yandex._mcp import RO` vs resources `from ..._deps import RO`)
- Create: `docs/conventions/resources.md`
- Test: affected model/cli/mcp tests

**Interfaces:**
- Produces: consistent model conventions; a written resource convention.

- [ ] **Step 1: `me` models inherit `APIModel`**

In `tracker/me/models.py` and `wiki/me/models.py`, change the base from `pydantic.BaseModel` to `from ycli.yandex.models import APIModel`. (`forms/me` already does.) This adds `extra="ignore"` + `populate_by_name`.

- [ ] **Step 2: Delete the dead file**

```bash
git rm src/ycli/yandex/forms/_models.py
grep -rn 'forms._models' src tests   # expect no hits
```

- [ ] **Step 3: Rename the surveys models to the convention**

In `forms/surveys/models.py`, the flat `RootModel` list should be `SurveyList` and any envelope should be `SurveysResponse` (matching `XList = flat RootModel`, `XResponse = envelope` used elsewhere). Update all importers (client/cli/mcp/tests). This renames model classes only — NOT CLI/MCP names — so snapshots are unaffected.

- [ ] **Step 4: Reconcile the `RO` import path**

Pick one canonical path. Recommended: resources import `RO` from `_deps` (already re-exported via B3 `__all__`), and the scaffold template (`scripts/new_endpoint.py`) is updated to match (`from ycli.yandex.<domain>._deps import RO, TAGS, <domain>_client`). Verify the scaffold's generated MCP module matches a real sibling.

- [ ] **Step 5: Write `docs/conventions/resources.md`**

Capture the rules ARCHITECTURE.md omits: every model inherits `APIModel` (incl. `me`); list-model naming (`XList = RootModel[list[X]]` flat; envelopes `XResponse`); the `RO`/`TAGS`/`<domain>_client` import path; when a `_raw`/`full` accessor is offered; the MCP metadata standard pointer (Task E4). Link it from `ARCHITECTURE.md` and `CLAUDE.md`.

- [ ] **Step 6: Verify**

Run: `uv run pytest && uv run lint-imports && uv run pytest tests/test_snapshots.py -v`
Expected: green; snapshots unchanged (only class renames).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor(conventions): me models -> APIModel; drop dead forms/_models; rename surveys models; resources.md"
```

---

## Phase E — CLI / MCP / output surface (snapshot-changing)

### Task E1: `mcp` Typer sub-app; delete `mcp_launcher.py`

**Files:**
- Create: `src/ycli/mcp_cli.py`
- Delete: `src/ycli/mcp_launcher.py`
- Modify: `src/ycli/cli.py` (mount sub-app, drop launcher)
- Modify: `plugins/yandex-360/.mcp.json` (args `["…","ycli","mcp"]` → `["…","ycli","mcp","start"]`)
- Regenerate: `tests/snapshots/cli_tree.txt`
- Modify: `tests/test_yandex_cli.py` (`["mcp"]`→`["mcp","start"]`), the plugin `.mcp.json` test
- Test: new `mcp start` / `mcp methods` behavior

**Interfaces:**
- Produces: `ycli mcp start` (runs the server), `ycli mcp methods` (lists tool names). ARCH-3 preserved (lazy `import ycli.mcp`, never `fastmcp` directly in `mcp_cli.py`).

- [ ] **Step 1: Write the failing CLI tests**

`tests/test_yandex_cli.py` (adapt existing mcp test):
```python
def test_mcp_start_launches_server(monkeypatch):
    called = {}
    import ycli.mcp_cli as m
    monkeypatch.setattr("ycli.mcp.main", lambda: called.setdefault("ran", True))
    from typer.testing import CliRunner
    from ycli.cli import app
    res = CliRunner().invoke(app, ["mcp", "start"])
    assert res.exit_code == 0 and called.get("ran")

def test_mcp_methods_lists_tool_names():
    from typer.testing import CliRunner
    from ycli.cli import app
    res = CliRunner().invoke(app, ["mcp", "methods"])
    assert res.exit_code == 0
    assert "tracker_issues_get" in res.stdout  # a known namespaced tool
```

- [ ] **Step 2: Run (fails)**

Run: `uv run pytest tests/test_yandex_cli.py -k mcp -v`
Expected: FAIL (`mcp_cli` missing; `mcp start` unknown).

- [ ] **Step 3: Create `mcp_cli.py`**

```python
"""``ycli mcp`` sub-app: run the server and list its tools. Importable without the mcp extra."""
from __future__ import annotations

import typer

app = typer.Typer(name="mcp", help="Read-only MCP server control.", no_args_is_help=True)

_MISSING = (
    "The MCP server requires the 'mcp' extra. Install it with: "
    "uv add 'yandex-cli[mcp]'  (or: uv tool install 'yandex-cli[mcp]')."
)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager import, --help stays extra-free)."""


@app.command()
def start() -> None:
    """Run the read-only MCP server over stdio (tools namespaced wiki_*, tracker_*, forms_*)."""
    try:
        from ycli.mcp import main as run_server
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc
    run_server()


@app.command()
def methods() -> None:
    """List the MCP tool names exposed by the server."""
    import asyncio

    try:
        from fastmcp import Client

        from ycli.mcp import mcp
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc

    async def _list() -> None:
        async with Client(mcp) as client:
            for tool in sorted(t.name for t in await client.list_tools()):
                typer.echo(tool)

    asyncio.run(_list())
```

- [ ] **Step 4: Mount it; delete the launcher**

In `cli.py`: replace `from ycli.mcp_launcher import launch_mcp_server` + `app.command(name="mcp")(launch_mcp_server)` with `from ycli.mcp_cli import app as mcp_app` + `app.add_typer(mcp_app)`. Then `git rm src/ycli/mcp_launcher.py`.

- [ ] **Step 5: Update the plugin config + its test**

In `plugins/yandex-360/.mcp.json`, change the server args from `[..., "ycli", "mcp"]` to `[..., "ycli", "mcp", "start"]`. Update the test that asserts the plugin args (`test_plugin_mcp_declares_readonly_server` or similar).

- [ ] **Step 6: Regenerate snapshots (on purpose — ARCH-6)**

Run: `uv run python -m tests.snapshots --update`
Expected: `tests/snapshots/cli_tree.txt` gains `mcp`, `mcp methods`, `mcp start`; loses bare `mcp`. Review the diff is exactly that.

- [ ] **Step 7: Verify**

Run: `uv run pytest && uv run lint-imports`
Expected: green; import-linter intact (`mcp_cli` not in ARCH-3 forbidden sources; it imports `ycli.mcp` lazily, never `fastmcp` at module top).

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat(cli): mcp Typer sub-app (mcp start/methods); delete mcp_launcher; regen snapshots"
```

### Task E2: Remove the Tracker deeplink (ARCH-5 leak)

**Files:**
- Modify: `src/ycli/output.py` (drop `_KEY_RE` + the link branch)
- Modify: `tests/test_output_links.py`, `tests/test_output_strategies.py`
- Modify: `CLAUDE.md` (note deeplink deferral)

**Interfaces:**
- Produces: `PrettyStrategy._cell` returns bare text (no hardcoded URL).

- [ ] **Step 1: Update the failing tests**

In `tests/test_output_links.py`, change the assertion that `ABC-1` becomes `[link=https://tracker.yandex.ru/ABC-1]…` to expect bare `ABC-1`. Same for the link case in `tests/test_output_strategies.py`. (If `test_output_links.py` becomes trivial, fold its remaining cases into `test_output_strategies.py`.)

- [ ] **Step 2: Run (fails)**

Run: `uv run pytest tests/test_output_links.py tests/test_output_strategies.py -v`
Expected: FAIL (still emits the link).

- [ ] **Step 3: Strip the deeplink**

In `output.py`: delete `_KEY_RE`, and the `is_key`/`link` plumbing that only fed the Tracker URL. `_cell` simplifies to:
```python
    def _cell(self, value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        if value is None:
            return ""
        return str(value)
```
Remove the now-unused `is_key`/`link` params threaded through `_prettify`/`_kv_table`/`_list_table`/`render` (and the `link=console.is_terminal` argument). `import re` can go if unused.

- [ ] **Step 4: Note the deferral in CLAUDE.md**

Add a short line under output/rendering: a general per-model deeplink mechanism is deferred; no surface hardcodes a UI URL (keeps ARCH-5 clean).

- [ ] **Step 5: Verify (ARCH-5 clean)**

Run: `uv run pytest && uv run pytest tests/test_architecture.py -k arch5 -v`
Expected: green; no hardcoded `tracker.yandex.ru` in `output.py`.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor(output): remove Tracker-only deeplink (ARCH-5 leak); defer general deeplink design"
```

### Task E3: Decompose `PrettyStrategy` (RichCell / RichTableBuilder)

**Files:**
- Modify: `src/ycli/output.py`
- Test: `tests/test_output_strategies.py` (add helper unit tests)

**Interfaces:**
- Produces: `RichCell` (value→text), `RichTableBuilder` (table assembly); `_list_table` split into `_list_of_dicts_table`/`_list_of_scalars_table`. Behavior identical.

- [ ] **Step 1: Write failing unit tests for the helpers**

```python
from ycli.output import RichCell

def test_richcell_renders_none_as_blank_and_nested_as_json():
    assert RichCell.of(None).text == ""
    assert RichCell.of({"a": 1}).text == '{"a": 1}'
    assert RichCell.of("DE-1").text == "DE-1"
```

- [ ] **Step 2: Run (fails)**

Run: `uv run pytest tests/test_output_strategies.py -k richcell -v`
Expected: FAIL (`RichCell` missing).

- [ ] **Step 3: Implement the helpers + split `_list_table`**

In `output.py`:
```python
class RichCell:
    """A single rendered cell: value → display text."""

    def __init__(self, text: str) -> None:
        self.text = text

    @classmethod
    def of(cls, value: Any) -> "RichCell":
        if isinstance(value, (dict, list)):
            return cls(json.dumps(value, ensure_ascii=False))
        if value is None:
            return cls("")
        return cls(str(value))


class PrettyStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
        console.print(self._prettify(result.model_dump(by_alias=True, mode="json")))

    def _prettify(self, data: Any) -> Any:
        if isinstance(data, list):
            return self._list_table(data)
        if isinstance(data, dict):
            return self._kv_table(data)
        return str(data)

    def _kv_table(self, data: dict[str, Any]) -> Table:
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column(style="cyan", no_wrap=True)
        table.add_column(overflow="fold")
        for key, value in data.items():
            table.add_row(str(key), RichCell.of(value).text)
        return table

    def _list_table(self, items: list[Any]) -> Table:
        if items and isinstance(items[0], dict):
            return self._list_of_dicts_table(items)
        return self._list_of_scalars_table(items)

    def _list_of_dicts_table(self, items: list[dict[str, Any]]) -> Table:
        table = Table()
        columns = list(items[0].keys())
        for column in columns:
            table.add_column(str(column), style="cyan", overflow="fold")
        for item in items:
            table.add_row(*[RichCell.of(item.get(c)).text for c in columns])
        return table

    def _list_of_scalars_table(self, items: list[Any]) -> Table:
        table = Table()
        table.add_column("value", overflow="fold")
        for item in items:
            table.add_row(RichCell.of(item).text)
        return table
```
(A `RichTableBuilder` is optional — introduce it only if it earns its keep after the split; the split above already drops `_list_table` to CC≤2. If you add it, give it a unit test.)

- [ ] **Step 4: Verify behavior unchanged**

Run: `uv run pytest tests/test_output_strategies.py -v && uv run pytest`
Expected: green; identical rendered output for existing cases; 100% coverage (each new helper exercised).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(output): decompose PrettyStrategy into RichCell + split list-table builders"
```

### Task E4: MCP metadata standard

**Files:**
- Modify: `scripts/new_endpoint.py` (MCP template comment), `docs/conventions/resources.md` (metadata section)
- Optionally: `tests/test_architecture.py` (assert every tool has description + output schema)

**Interfaces:**
- Produces: a written standard; optionally an enforcing test. No tool bodies change (all 25 already comply).

- [ ] **Step 1: (Optional) Write the failing metadata test**

In `tests/test_architecture.py`:
```python
@pytest.mark.asyncio
async def test_every_mcp_tool_has_description_and_output_schema():
    from fastmcp import Client
    from ycli.mcp import mcp
    async with Client(mcp) as client:
        for tool in await client.list_tools():
            assert tool.description, tool.name
            assert tool.outputSchema is not None, tool.name
```

- [ ] **Step 2: Run (expect pass — standard already met)**

Run: `uv run pytest tests/test_architecture.py -k mcp_tool_has -v`
Expected: PASS (docstring→description and return-type→output_schema are auto-derived). If any tool fails, fix that tool's docstring/return annotation.

- [ ] **Step 3: Document the standard**

In `docs/conventions/resources.md` (MCP section): every tool sets `name` (snake_case `<resource>_<verb>`), a one-line-first docstring (→ `description`, the LLM's selector — required), a concrete return type (→ `output_schema`), `annotations={**RO,"title":…}`, `tags`. `description`/`output_schema` are auto-derived — never set by hand. Add a one-line comment to the scaffold's MCP template stating the docstring IS the description and the return type IS the output schema.

- [ ] **Step 4: Verify**

Run: `uv run pytest && uv run pytest tests/test_snapshots.py -v`
Expected: green; snapshots unchanged (names only; metadata not snapshotted).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs(mcp): write tool-metadata standard; scaffold comment; assert description+output schema"
```

---

## Phase F — Infra, meta & docs (README LAST)

### Task F1: graphify code graph (gitignored local index)

**Files:**
- Create: `.graphify/` config (gitignored)
- Modify: `.gitignore` (`/.graphify/`)
- Create: `.claude/commands/codegraph-regen.md` (regenerate command)
- Modify: `CONTRIBUTING.md`/`docs/` note on building the graph

**Decision:** `.graphify/` is a **gitignored local navigation index** (the semantic pass is nondeterministic — committing it would fight the reproducible-artifact rule and the 100%-coverage path). It's rebuilt on demand via the command.

- [ ] **Step 1: Confirm graphify is installed and read its CLI**

Run: `graphify --help` (installed via `uv tool install`)
Expected: usage. Note the build command, the config-file location flag, and how to set the model/provider.

- [ ] **Step 2: Configure graphify under `.graphify/`**

Create the graphify config in `.graphify/` targeting `src/`, with the semantic model set to **GLM-5.2** via OpenRouter (`OPENROUTER_API_KEY` from env — never hardcode). Pin the model + prompt for reproducibility. Verify current GLM-5.2 availability/pricing on OpenRouter at implementation time.

- [ ] **Step 3: Build the graph once**

Run the graphify build over `src/`; confirm `.graphify/` gets `graph.json` + report. Inspect that the Leiden communities map sensibly (e.g. a pagination cluster, a transport cluster).

- [ ] **Step 4: Gitignore + command + verify clean tree**

Add `/.graphify/` to `.gitignore`. Create `.claude/commands/codegraph-regen.md` documenting the exact rebuild command. Run `git status` — expect `.graphify/` untracked-and-ignored, only `.gitignore` + the command file staged.

- [ ] **Step 5: Commit**

```bash
git add .gitignore .claude/commands/codegraph-regen.md CONTRIBUTING.md
git commit -m "chore(graph): graphify local code index (.graphify, gitignored) + /codegraph-regen"
```

### Task F2: Seed the drift log

**Files:**
- Create: entries under `.claude/drift-log/` (via the `core:creating-drift-logs` skill)
- Modify: `CLAUDE.md` (one-line nudge)

- [ ] **Step 1: Capture recurring conventions as drift entries**

Using the `core:creating-drift-logs` skill, write entries for the conventions this/prior rounds surfaced that the codebase enforces or should: composition-root DI (`ClientFactory`), serialization confinement (ARCH-4 + the `json.dumps` gap just closed), the `from_env` purge, the `@cache` MCP factory, full self-documenting names, snapshot discipline.

- [ ] **Step 2: Add the CLAUDE.md nudge**

One line: "When a session reveals a convention the codebase doesn't yet enforce, capture it via `core:creating-drift-logs` before ending."

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "docs(drift): seed drift log with recurring round-2/3 conventions; nudge in CLAUDE.md"
```

### Task F3: Helper commands `/snapshot-regen` + `/release-checklist`

**Files:**
- Create: `.claude/commands/snapshot-regen.md`, `.claude/commands/release-checklist.md`

- [ ] **Step 1: `/snapshot-regen`**

Document: run `uv run python -m tests.snapshots --update`, then `git diff tests/snapshots/` and require the diff be intentional (ARCH-6). Follow `docs/conventions/skills-and-commands.md`.

- [ ] **Step 2: `/release-checklist`**

Encode the post-release steps: after a merge to main releases, run `uv lock` + a `build:` commit (uv.lock drift); and the never-skip-ci rule incl. the GitHub-UI squash-title blind spot the `git_guard` hook can't see.

- [ ] **Step 3: Verify the commands load**

Confirm both files follow the command frontmatter convention (compare to `/new-endpoint`, `/arch-review`).

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/
git commit -m "feat(commands): /snapshot-regen and /release-checklist"
```

### Task F4: (Optional) doc-drift guard

**Files:**
- Modify: `tests/test_architecture.py` (or a new `tests/test_docs.py`), `ARCHITECTURE.md` (if enforced as ARCH-11)

- [ ] **Step 1: Decide enforce-vs-command**

If enforcing: add a test asserting purged idioms (`from_env`, `@uplink.timeout`) do NOT appear in `README.md`/`docs/**` code blocks. If documenting ARCH-11, add it to `ARCHITECTURE.md` in the same commit. If keeping lighter, fold the grep into `/arch-review` instead.

- [ ] **Step 2: Implement + verify**

Run: `uv run pytest tests/test_architecture.py -k doc_drift -v`
Expected: initially FAILS on the README `from_env` (fixed in F6) — so either land F4 after F6, or have F4 assert against `src/`+`docs/` and let F6 fix the README. Sequence F4 immediately before F6 if enforcing.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "test(docs): guard against purged idioms leaking into docs (ARCH-11)"
```

### Task F5: Minimalist badges

**Files:**
- Modify: `README.md` (badge block, lines ~9–14)

- [ ] **Step 1: Replace the badge block**

Swap the six `for-the-badge` badges for a minimal `flat-square` set in one neutral grey, add the DeepWiki + PyPI badges, drop the loud MCP/Claude-Code marketing badges:
```markdown
[![CI](https://img.shields.io/github/actions/workflow/status/bim-ba/ycli/ci.yml?branch=main&style=flat-square&label=ci&color=555)](https://github.com/bim-ba/ycli/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-555?style=flat-square)](https://github.com/bim-ba/ycli)
[![PyPI](https://img.shields.io/pypi/v/yandex-cli?style=flat-square&color=555&label=pypi)](https://pypi.org/project/yandex-cli/)
[![Python](https://img.shields.io/badge/python-3.12%2B-555?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-555?style=flat-square)](LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/bim-ba/ycli)
```

- [ ] **Step 2: Verify the PyPI slug + render**

Confirm `yandex-cli` is the PyPI project name. Preview the README locally if possible.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs(readme): minimalist flat-square badges + DeepWiki + PyPI"
```

### Task F6: README + all-docs audit; regenerate the demo gif (LAST)

> Runs AFTER every surface change (E1's `mcp start`) is final.

**Files:**
- Modify: `README.md` (fix `from_env` drift at line ~104; update any changed commands/flags)
- Modify: `docs/demo/demo.tape` (if the demo invokes `ycli mcp` → `ycli mcp start`), then regenerate `docs/assets/demo.gif`
- Sweep: all other `.md` (`docs/**`, `plugins/**`, `CLAUDE.md`, `ARCHITECTURE.md`)

- [ ] **Step 1: Fix the `from_env` drift**

`README.md` line ~104 shows `TrackerClient.from_env()` — purged by ARCH-7. Replace with the raw-arg constructor (`TrackerClient(oauth_token=…, organization_id=…)`) or an `AppContext`-based example matching the real SDK.

- [ ] **Step 2: Sweep every `.md` for stale commands/flags/examples**

Grep docs for: `from_env`, `@uplink.timeout`, bare `ycli mcp` (now `ycli mcp start`), old badge styles, the `ycli.models`/`ycli.yandex.settings` paths (now moved), `_cell`/deeplink claims, any `SurveyCollection` references. Fix each to match the final code.

- [ ] **Step 3: Regenerate the demo gif from source**

If `docs/demo/demo.tape` invokes `ycli mcp`, update it to `ycli mcp start`. Regenerate via the committed path (`.github/workflows/demo.yml` / vhs against `demo.tape`) — never hand-edit the gif. Confirm `docs/assets/demo.gif` is the regenerated artifact.

- [ ] **Step 4: Verify docs + final full suite**

Run: `uv run pytest && uv run lint-imports && uv run ruff check . && uv run ruff format --check .`
Expected: all green. If F4's doc-drift guard is enforced, it now passes (README fixed).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs: fix from_env drift, audit all .md, regenerate demo gif from demo.tape"
```

---

## Self-Review

**1. Spec coverage:**
- A (tooling) → A1–A4 ✅ · B (composition) → B1–B4 ✅ · C (transport/status/auth) → C1–C2 ✅ (C1 folds the seam) · D (dedup/conventions/ARCH-4) → D1–D4 ✅ (the `_deps` collapse moved into B3 per the spec's note that B3+D3 pair; transitions D2; single-page D3; conventions D4) · E (surface) → E1–E4 ✅ · F (infra/meta) → F1–F6 ✅. The `count` CLI/MCP alignment (spec D7, optional) is intentionally omitted as low-priority — flag to the user if they want it in scope.

**2. Placeholder scan:** No "TBD/handle edge cases". Tasks D2/D3 include explicit "read first" steps because they touch files not loaded into the plan author's context; their design + code sketch + verification are concrete. F1 graphify and F4 doc-drift carry explicit decisions (gitignored index; enforce-before-F6).

**3. Type consistency:**
- `ClientFactory.build(client_cls, credentials, config)` — used identically in B3 (`_mcp.make_cached_client`, `AppContext._client`) and C2 (`ServiceProbe.run`). ✅
- `app_config()` defined in `_mcp.py` (B3), re-exported via `_deps.__all__` (B3), consumed in B4 + leaf mcp tools. ✅
- `AppContext.config` (B3) consumed in B4 CLI bodies. ✅
- `Transport._raise_typed` / `Transport._authorization` (C1) — test + session wiring agree. ✅
- `RawMapping` (D1) / `TransitionList` (D2) — RootModel models rendered via `Serializer.serialize`. ✅
- `collect_single_page(page_fn, *, extract, wrap, limit)` (D3). ✅
- `RichCell.of(value).text` (E3) — used in all four table builders + the unit test. ✅
- `ycli.yandex.models` (B1) and `ycli.settings` (B2) import paths are used consistently from B onward. ✅

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-29-round-3-architecture-and-tooling.md`. Two execution options:

1. **Subagent-Driven (recommended)** — fresh implementer per task, two-stage review (spec + quality) between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints.

Round-3 depends on round-2 (PR #10): start execution only after round-2 merges to main, then rebase this branch onto main.
