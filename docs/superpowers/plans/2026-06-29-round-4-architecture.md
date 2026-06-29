# Round-4 Architecture Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drop the one-off `RawMapping`/`full` raw accessor, turn `status` and `mcp` into proper packages (status gains a `status_get` MCP tool and returns the bare native `me`), tighten pagination types, and make the demo GIF render real CLI output from committed fixtures.

**Architecture:** Six independent tasks (T1–T6), each a single commit ending in a green gate. Public-surface changes regenerate `tests/snapshots/` on purpose (ARCH-6); each invariant edit changes `ARCHITECTURE.md` together with its enforcing check. The 100% coverage gate stays green throughout — dead code is deleted with its dead tests.

**Tech Stack:** Python ≥3.12 · uv · uplink+requests · typer · fastmcp (read-only) · pydantic v2 · ruff · ty 0.0.55 · pytest + `responses` · vhs.

**Spec:** `docs/superpowers/specs/2026-06-29-round-4-architecture-design.md`

## Global Constraints

- `client.py` / `_base.py` modules MUST NOT use `from __future__ import annotations` (uplink reads runtime annotations). Other modules may.
- Credentials enter only at a composition root (`Credentials()`/`AppConfig()` for CLI via `AppContext`; the `_deps` cached providers for MCP) as raw `oauth_token`/`organization_id`. No `from_env`. Never hardcode `YANDEX_ID_*` (ARCH-5/7/8).
- MCP is read-only (ARCH-3): a tool's verb (last `_`-segment) must be in `READ_VERBS = {"get","list","count","search","descendants","meta"}` (note: `"full"` is removed in T2) and carry `readOnlyHint=True` via the `RO` annotation; no `mcp.py` calls a client write method.
- Output only via `output.Serializer.serialize(...)` (ARCH-4).
- Self-documenting names, no abbreviations.
- 100% coverage: `uv run pytest` enforces `--cov-fail-under=100`.
- Final gate for every task: `uv run ruff format --check . && uv run ruff check . && uv run lint-imports && uv run ty check && uv run pytest`.
- Commits end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Branch `refactor/round-4-architecture` (already created off main). No direct push to main. No skip-ci token in any commit message.

---

### Task 1: `ycli/mcp/` package (W-C)

Turn the two root MCP modules into a package. The package `__init__.py` MUST stay free of a top-level `fastmcp` import so the base install (no `mcp` extra) can import `ycli.mcp.cli` — the server lives in `server.py`, exposed lazily.

**Files:**
- Create: `src/ycli/mcp/__init__.py` (lazy re-export, fastmcp-free)
- Create: `src/ycli/mcp/server.py` (the FastMCP server — body of the old `src/ycli/mcp.py`)
- Create: `src/ycli/mcp/cli.py` (the `ycli mcp` Typer app — body of the old `src/ycli/mcp_cli.py`)
- Create: `src/ycli/mcp/__main__.py` (so `python -m ycli.mcp` runs the server)
- Delete: `src/ycli/mcp.py`, `src/ycli/mcp_cli.py`
- Modify: `src/ycli/cli.py:14` import
- Modify: `ARCHITECTURE.md` ARCH-3 prose
- Test: `tests/test_yandex_mcp.py`, `tests/test_yandex_cli.py` (existing — must stay green unchanged)

**Interfaces:**
- Produces: `from ycli.mcp import mcp, main` (lazy via `__getattr__`); `from ycli.mcp.cli import app`; `python -m ycli.mcp`. T3 mounts a status subserver in `server.py`.
- Consumes: nothing new.

- [ ] **Step 1: Add a base-install guard test (fastmcp-free import path)**

Add to `tests/test_yandex_mcp.py`:

```python
def test_base_install_imports_cli_without_fastmcp():
    """`ycli.mcp.cli` (and `ycli.cli`) must import without pulling fastmcp — base install."""
    import subprocess
    import sys

    code = "import ycli.cli, ycli.mcp.cli, sys; assert 'fastmcp' not in sys.modules"
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_yandex_mcp.py::test_base_install_imports_cli_without_fastmcp -v`
Expected: FAIL — `ycli.mcp.cli` does not exist yet (ModuleNotFoundError).

- [ ] **Step 3: Create `src/ycli/mcp/server.py`** (verbatim body of the current `src/ycli/mcp.py`)

```python
"""Root Yandex 360 FastMCP server — mounts the per-domain subservers.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per domain: ``wiki_*``, ``tracker_*``, ``forms_*``. Reads-only.
"""

from fastmcp import FastMCP

from ycli.log import configure
from ycli.settings import AppConfig
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp

mcp = FastMCP(
    "yandex",
    instructions=(
        "Read-only access to Yandex 360: Tracker (issues, comments, worklog, …), "
        "Wiki (pages, attachments), and Forms. Tools are namespaced wiki_*, tracker_*, "
        "forms_*, and are all read-only — create/update happens via the ycli CLI/SDK, not "
        "here. Credentials come from the YANDEX_ID_OAUTH_TOKEN and "
        "YANDEX_ID_ORGANIZATION_ID environment variables."
    ),
)
mcp.mount(wiki_mcp, namespace="wiki")
mcp.mount(tracker_mcp, namespace="tracker")
mcp.mount(forms_mcp, namespace="forms")


def main() -> None:
    """Run the root server over stdio (the console-script entry point).

    Example:
        >>> main()  # doctest: +SKIP
    """
    configure(
        level=AppConfig().log_level
    )  # match the CLI: single stderr sink, stdout stays clean for the protocol
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
```

- [ ] **Step 4: Create `src/ycli/mcp/__init__.py`** (lazy, fastmcp-free)

```python
"""The ``ycli mcp`` surface — the read-only FastMCP server plus its CLI sub-app.

``__init__`` stays import-light so the base install (no ``mcp`` extra) can load
``ycli.mcp.cli`` without importing fastmcp; ``mcp`` and ``main`` resolve lazily on
attribute access, preserving ``from ycli.mcp import mcp, main`` for every call site.
"""

from __future__ import annotations

from typing import Any

__all__ = ["main", "mcp"]


def __getattr__(name: str) -> Any:
    if name in {"mcp", "main"}:
        from ycli.mcp import server

        return getattr(server, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

- [ ] **Step 5: Create `src/ycli/mcp/cli.py`** (verbatim body of the current `src/ycli/mcp_cli.py`)

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

- [ ] **Step 6: Create `src/ycli/mcp/__main__.py`**

```python
"""``python -m ycli.mcp`` — run the read-only MCP server over stdio."""

from ycli.mcp.server import main

if __name__ == "__main__":  # pragma: no cover
    main()
```

- [ ] **Step 7: Delete the old modules**

```bash
git rm src/ycli/mcp.py src/ycli/mcp_cli.py
```

- [ ] **Step 8: Update `src/ycli/cli.py:14`**

Old:
```python
from ycli.mcp_cli import app as mcp_app
```
New:
```python
from ycli.mcp.cli import app as mcp_app
```

- [ ] **Step 9: Update `ARCHITECTURE.md` ARCH-3 prose**

In the ARCH-3 bullet, replace the opening sentence:
```
- **ARCH-3 — MCP is read-only.** `fastmcp` is imported only in modules named `mcp.py`. Every MCP
```
with:
```
- **ARCH-3 — MCP is read-only.** `fastmcp` is imported only in modules named `mcp.py` and in the
  `ycli.mcp` server package (`src/ycli/mcp/server.py`; its `__init__.py` stays fastmcp-free so the
  base install loads the CLI sub-app without the extra). Every MCP
```
(Note: the import-linter contract in `pyproject.toml` already permits this — `ycli.mcp*` is not in the ARCH-3 `source_modules` forbidden list — so only the prose changes. Confirm with `uv run lint-imports` in Step 11.)

- [ ] **Step 10: Run the base-install guard + the MCP server tests**

Run: `uv run pytest tests/test_yandex_mcp.py tests/test_yandex_cli.py -v`
Expected: PASS — including `test_base_install_imports_cli_without_fastmcp`, `test_root_mounts_all_domains_with_namespaces` (still 25 tools), `test_mcp_start_launches_server` (patches `ycli.mcp.main`), `test_mcp_methods_lists_tool_names`.

- [ ] **Step 11: Full gate + smoke test**

Run: `uv run ruff format --check . && uv run ruff check . && uv run lint-imports && uv run ty check && uv run pytest`
Expected: all green. Then build-free smoke check:
Run: `uv run python -c "from ycli.mcp import mcp, main; from ycli.mcp.cli import app; print('ok')"`
Expected: `ok`. And `uv run python -m ycli.mcp --help`-equivalent is not applicable (server runs stdio); instead verify the entry resolves: `uv run python -c "import ycli.mcp.__main__"` → no error.

- [ ] **Step 12: Commit**

```bash
git add -A
git commit -m "refactor: move the MCP server + CLI into a ycli.mcp package

Server lives in ycli/mcp/server.py; the package __init__ stays fastmcp-free and
re-exports mcp/main lazily so the base install loads ycli.mcp.cli without the extra.
python -m ycli.mcp runs the server via __main__. Updates ARCH-3 prose.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Remove `RawMapping` / `full` / `get_raw` / `issues_full` (W-A)

Delete the one-off raw accessor across all four surfaces and its tests, update the two invariants that mention it, and regenerate the snapshots.

**Files:**
- Modify: `src/ycli/yandex/models.py` (delete `RawMapping`)
- Modify: `src/ycli/yandex/tracker/issues/client.py` (delete `get_raw`)
- Modify: `src/ycli/yandex/tracker/issues/cli.py` (delete `full` command + `RawMapping` import)
- Modify: `src/ycli/yandex/tracker/issues/mcp.py` (delete `issues_full` tool + unused `Any` import if newly unused)
- Modify: `tests/yandex/tracker/issues/test_client.py`, `test_mcp.py`, `test_cli.py`, `tests/yandex/tracker/test_mcp.py`, `tests/test_yandex_mcp.py`
- Modify: `tests/test_architecture.py` (`READ_VERBS`)
- Modify: `ARCHITECTURE.md` (ARCH-4), `docs/conventions/resources.md` (§4)
- Regenerate: `tests/snapshots/mcp_tools.txt`, `tests/snapshots/cli_tree.txt`

**Interfaces:**
- Produces: a smaller public surface (no `tracker issues full` CLI, no `issues_full` tool, no `get_raw` SDK method, no `RawMapping`). T3 re-adds one tool (`status_get`) restoring the MCP total to 25.

- [ ] **Step 1: Delete the dead tests first (red baseline)**

In `tests/yandex/tracker/issues/test_client.py` delete `test_get_raw_returns_dict` (the whole `@responses.activate` function asserting `_client().get_raw("DE-1") == {...}`).

In `tests/yandex/tracker/issues/test_mcp.py`:
- Delete `test_issues_full_tool_returns_raw_dict` (the function calling `client.call_tool("issues_full", ...)`).
- In `test_issue_tools_registered_read_only`, change the asserted set from
  `{"issues_get", "issues_full", "issues_list", "issues_search", "issues_count"}` to
  `{"issues_get", "issues_list", "issues_search", "issues_count"}`.

In `tests/yandex/tracker/issues/test_cli.py` delete both `test_full_renders_raw_dict_as_json` and `test_full_renders_raw_dict_as_yaml` (the latter holds the in-function `import yaml`; deleting it removes that smell — do NOT hoist `import yaml` to module top, no surviving test uses yaml, it would be an unused import).

In `tests/yandex/tracker/test_mcp.py`:
- In `test_all_fourteen_read_tools_registered`, remove `"issues_full",` from the asserted set.
- Rename the function to `test_all_thirteen_read_tools_registered` and update the module docstring line 1 from `14 reads-only tools` to `13 reads-only tools`.

In `tests/test_yandex_mcp.py`, in `test_root_mounts_all_domains_with_namespaces` change:
```python
    assert len([n for n in names if n.startswith("tracker_")]) == 14
```
to
```python
    assert len([n for n in names if n.startswith("tracker_")]) == 13
```
and
```python
    assert len(names) == 25
```
to
```python
    assert len(names) == 24
```
(T3 will restore this to 25 by adding `status_get`.)

- [ ] **Step 2: Run the suite to confirm the deleted-feature tests are gone and the rest still reference live code**

Run: `uv run pytest tests/yandex/tracker -q`
Expected: FAIL — surviving tests still pass, but the source still defines `full`/`get_raw`/`issues_full`, so the snapshot tests and `test_all_thirteen...`/count asserts now mismatch (source has 14 tracker tools, tests expect 13). This is the red state that the source deletion (next steps) turns green.

- [ ] **Step 3: Delete `RawMapping` from `src/ycli/yandex/models.py`**

Remove the class and the now-unused `RootModel` / `Any` imports:
```python
from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel
```
becomes
```python
from pydantic import BaseModel, ConfigDict
```
and delete:
```python
class RawMapping(RootModel[dict[str, Any]]):
    """Wraps an unmodeled API dict so it renders through the Serializer (honoring --format)."""
```

- [ ] **Step 4: Delete `get_raw` from `src/ycli/yandex/tracker/issues/client.py`**

Remove the whole method (the `@uplink.returns.json()` + `@uplink.get("issues/{key}")` + `def get_raw(...)` block with its docstring).

- [ ] **Step 5: Delete the `full` command from `src/ycli/yandex/tracker/issues/cli.py`**

Remove the `full` command:
```python
@app.command()
def full(ctx: typer.Context, key: KeyArg) -> None:
    """Print the raw API dict for KEY (no pydantic projection)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        RawMapping(app_ctx.tracker.issues.get_raw(key)), app_ctx.strategy, app_ctx.console
    )
```
and remove its now-unused import line:
```python
from ycli.yandex.models import RawMapping
```

- [ ] **Step 6: Delete the `issues_full` tool from `src/ycli/yandex/tracker/issues/mcp.py`**

Remove:
```python
@mcp.tool(
    name="issues_full", annotations={**RO, "title": "Get full Tracker issue (raw)"}, tags=TAGS
)
def full(key: str, client: TrackerClient = Depends(tracker_client)) -> dict[str, Any]:
    """A single Tracker issue as a raw dict (all fields)."""
    return client.issues.get_raw(key)
```
Then check whether `Any` is still used in the file (the `from typing import Any` import). After removing `full`, grep the file: if `Any` no longer appears, delete `from typing import Any`.

- [ ] **Step 7: Update `READ_VERBS` in `tests/test_architecture.py:24`**

Old:
```python
READ_VERBS = {"get", "list", "count", "full", "search", "descendants", "meta"}
```
New:
```python
READ_VERBS = {"get", "list", "count", "search", "descendants", "meta"}
```

- [ ] **Step 8: Update ARCH-4 in `ARCHITECTURE.md`**

Replace:
```
  strategies live only in `output.py`. Unmodeled API dicts are wrapped in `RawMapping`
  (a `RootModel[dict]` in `ycli.yandex.models`) before being passed to the Serializer.
  *Carve-out:* a bare `print(int)` for a scalar `count` result is fine — it is not model
```
with:
```
  strategies live only in `output.py`. Every rendered value is a typed pydantic model — there
  is no raw-dict/`RawMapping` escape hatch.
  *Carve-out:* a bare `print(int)` for a scalar `count` result is fine — it is not model
```

- [ ] **Step 9: Remove §4 from `docs/conventions/resources.md`**

Delete the entire `## 4. Raw / full unpruned accessor (...)` section (its heading through just before `## 5. MCP tool-metadata standard`). Renumber the subsequent headings: `## 5.` → `## 4.`, `## 6.` → `## 5.`. Update any in-document cross-reference to those numbers if present (grep the file for `§4`/`§5`/`§6` / `section 5`).

- [ ] **Step 10: Regenerate the snapshots**

Run: `uv run python -m tests.snapshots --update`
Expected output: `wrote cli_tree.txt` and `wrote mcp_tools.txt`. Verify the diff removes exactly `tracker issues full` from `cli_tree.txt` and `tracker_issues_full` from `mcp_tools.txt` (and nothing else):
Run: `git diff tests/snapshots/`

- [ ] **Step 11: Full gate**

Run: `uv run ruff format --check . && uv run ruff check . && uv run lint-imports && uv run ty check && uv run pytest`
Expected: all green (24 MCP tools now; `test_arch3_mcp_tools_are_read_only` passes with no `_full` verb; `unused-ignore-comment` clean).

- [ ] **Step 12: Commit**

```bash
git add -A
git commit -m "feat!: remove the raw issues 'full' accessor and RawMapping

BREAKING CHANGE: drops the 'tracker issues full' CLI command, the issues_full MCP
tool, IssuesClient.get_raw, and the RawMapping model. Every resource is a typed model.
Updates ARCH-3 read-verb allow-list, ARCH-4, resources.md, and the surface snapshots.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: `status` package + native `me` + `status_get` MCP tool (W-B, W-F note, W-7)

Explode `src/ycli/yandex/status.py` into a package, drop `ServiceProbe` + identity lambdas, return the bare native `me`, and add a read-only `status_get` MCP tool.

**Files:**
- Create: `src/ycli/yandex/status/__init__.py`, `models.py`, `reporter.py`, `cli.py`, `mcp.py`
- Delete: `src/ycli/yandex/status.py`
- Modify: `src/ycli/mcp/server.py` (mount status subserver)
- Modify: `tests/test_yandex_mcp.py` (total 24→25, add `status_` assertion)
- Modify: `ARCHITECTURE.md` (ARCH-1 clarifying note)
- Regenerate: `tests/snapshots/mcp_tools.txt`
- Create: `tests/yandex/status/__init__.py`, `tests/yandex/status/test_mcp.py`
- Keep: `tests/yandex/test_status.py` (CLI behavior — must stay green unchanged)

**Interfaces:**
- Consumes: each domain's `me` client (`TrackerClient.me` etc.), the cached `_deps` providers (`tracker_client`, `wiki_client`, `forms_client`), `RO` from `ycli.yandex._mcp`.
- Produces: `from ycli.yandex.status import app` (the `auth` Typer app — unchanged import for `cli.py:18`); the `status_get` MCP tool (verb `get`, namespace `status`); `ServiceAuthStatus(service, valid, me, detail)`, `AuthReport(configured, organization_id, services)`, `StatusReporter(me_clients).report(configured=, organization_id=)`.

- [ ] **Step 1: Create the package `__init__.py`**

`src/ycli/yandex/status/__init__.py`:
```python
"""Cross-cutting auth-status surface — the `auth status` CLI plus the `status_get` MCP tool.

Not a `<domain>/<resource>` package (ARCH-1 four-surface symmetry does not apply): it
aggregates the three domains' `me` probes into one report.
"""

from ycli.yandex.status.cli import app

__all__ = ["app"]
```

- [ ] **Step 2: Create `models.py`**

`src/ycli/yandex/status/models.py`:
```python
"""Models for `ycli auth status` and the `status_get` MCP tool."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.forms.me.models import User as FormsMe
from ycli.yandex.models import APIModel
from ycli.yandex.tracker.me.models import Me as TrackerMe
from ycli.yandex.wiki.me.models import Me as WikiMe


class ServiceAuthStatus(APIModel):
    """One service's auth probe — the bare native `me` on success, else why it failed."""

    service: str
    valid: bool = False
    me: TrackerMe | WikiMe | FormsMe | None = None
    detail: str = ""


class AuthReport(APIModel):
    """Whether the env credentials are set and work, per service."""

    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = Field(default_factory=list)
```

Note: the three `me` models share a class name (`Me`/`Me`/`User`), hence the `as TrackerMe`/`as WikiMe`/`as FormsMe` aliases. The reporter passes model *instances* (not dumped dicts) so pydantic's smart-union keeps each one's concrete type.

- [ ] **Step 3: Create `reporter.py`**

`src/ycli/yandex/status/reporter.py`:
```python
"""Probe each service's identity endpoint and assemble an AuthReport (shared by CLI + MCP)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.status.models import AuthReport, ServiceAuthStatus

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ycli.yandex.models import APIModel


class MeProbe(Protocol):
    """Structural type for a domain `me` client: a zero-arg `get()` returning an API model."""

    def get(self) -> APIModel: ...


class StatusReporter:
    """Given each service's `me` client, probe identity and build a per-service AuthReport."""

    def __init__(self, me_clients: Mapping[str, MeProbe]) -> None:
        self._me_clients = me_clients

    def report(self, *, configured: bool, organization_id: str) -> AuthReport:
        services = [self._probe(name, client) for name, client in self._me_clients.items()]
        return AuthReport(
            configured=configured, organization_id=organization_id, services=services
        )

    @staticmethod
    def _probe(name: str, me_client: MeProbe) -> ServiceAuthStatus:
        try:
            me = me_client.get()
        except YandexAuthError:
            return ServiceAuthStatus(service=name, valid=False, detail="token invalid or expired")
        except YandexError as exc:
            return ServiceAuthStatus(service=name, valid=False, detail=str(exc))
        return ServiceAuthStatus(service=name, valid=True, me=me)
```

- [ ] **Step 4: Create `cli.py`** (the `auth` app — builds clients via `AppContext`, which is typed, so no `ty: ignore`)

`src/ycli/yandex/status/cli.py`:
```python
"""`ycli auth status` — validate credentials against each service's identity endpoint."""

from __future__ import annotations

import typer
from pydantic import ValidationError

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.settings import Credentials
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)

_ENV_NAMES = {
    "oauth_token": "YANDEX_ID_OAUTH_TOKEN",
    "organization_id": "YANDEX_ID_ORGANIZATION_ID",
}


@app.command()
def status(ctx: typer.Context) -> None:
    """Report whether the env credentials are set and actually work, per service."""
    app_ctx = AppContext.from_typer_context(ctx)
    try:
        credentials = Credentials()  # ty: ignore[missing-argument]
    except ValidationError as exc:
        missing = ", ".join(
            _ENV_NAMES.get(str(e["loc"][0]), str(e["loc"][0])) for e in exc.errors()
        )
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        Serializer.serialize(
            AuthReport(configured=False, services=[]), app_ctx.strategy, app_ctx.console
        )
        raise typer.Exit(1) from None

    me_clients = {
        "tracker": app_ctx.tracker.me,
        "wiki": app_ctx.wiki.me,
        "forms": app_ctx.forms.me,
    }
    report = StatusReporter(me_clients).report(
        configured=True, organization_id=credentials.organization_id
    )
    Serializer.serialize(report, app_ctx.strategy, app_ctx.console)
    if not all(s.valid for s in report.services):
        raise typer.Exit(1)
```

- [ ] **Step 5: Create `mcp.py`** (read-only `status_get`)

`src/ycli/yandex/status/mcp.py`:
```python
"""Status FastMCP tool (read-only) — aggregate auth probe across all three services."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex._mcp import RO
from ycli.yandex.forms._deps import forms_client
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter
from ycli.yandex.tracker._deps import tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki._deps import wiki_client
from ycli.yandex.wiki.client import WikiClient

mcp = FastMCP("status")
TAGS: set[str] = {"status"}


@mcp.tool(name="get", annotations={**RO, "title": "Check Yandex 360 auth status"}, tags=TAGS)
def get(
    tracker: TrackerClient = Depends(tracker_client),
    wiki: WikiClient = Depends(wiki_client),
    forms: FormsClient = Depends(forms_client),
) -> AuthReport:
    """Probe each service's identity endpoint; report which credentials work.

    ``organization_id`` is left blank here — the per-service ``me`` already identifies the
    authenticated user; the CLI ``auth status`` carries the org id.
    """
    me_clients = {"tracker": tracker.me, "wiki": wiki.me, "forms": forms.me}
    return StatusReporter(me_clients).report(configured=True, organization_id="")
```

- [ ] **Step 6: Delete the old module**

```bash
git rm src/ycli/yandex/status.py
```

- [ ] **Step 7: Mount the status subserver in `src/ycli/mcp/server.py`**

Add the import alongside the others:
```python
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.status.mcp import mcp as status_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp
```
and add the mount after the three domain mounts:
```python
mcp.mount(wiki_mcp, namespace="wiki")
mcp.mount(tracker_mcp, namespace="tracker")
mcp.mount(forms_mcp, namespace="forms")
mcp.mount(status_mcp, namespace="status")
```

- [ ] **Step 8: Write the `status_get` MCP test**

Create `tests/yandex/status/__init__.py`:
```python
```
(empty file is fine — it is a test package, not a `yandex/` resource).

Create `tests/yandex/status/test_mcp.py`:
```python
"""status_get MCP tool — aggregates the three /me probes into one read-only report."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.status import mcp as status_mcp

TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_status_get_reports_all_valid(creds):
    responses.add(responses.GET, TRACKER_ME, json={"login": "alice"}, status=200)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    services = {s.service: s for s in result.data.services}
    assert services["tracker"].valid is True
    assert services["tracker"].me.login == "alice"
    assert services["forms"].me.email == "alice@x"


@responses.activate
async def test_status_get_marks_invalid_on_401(creds):
    responses.add(responses.GET, TRACKER_ME, status=401)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    services = {s.service: s for s in result.data.services}
    assert services["tracker"].valid is False
    assert services["tracker"].detail == "token invalid or expired"


async def test_status_get_is_read_only():
    async with Client(status_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "get" in tools
    assert tools["get"].annotations.readOnlyHint is True
```

Note: the cached `_deps` providers (`tracker_client` etc.) memoize via `functools.cache`; if a later test needs fresh creds, call `tracker_client.cache_clear()` — the existing per-domain MCP tests in the suite already exercise this pattern, so the cache is exercised consistently. These three tests use one cred set, so no clear is required.

- [ ] **Step 9: Update `tests/test_yandex_mcp.py` totals (restore to 25, add status)**

In `test_root_mounts_all_domains_with_namespaces` change the total back to 25 and add the status assertions:
```python
    assert "forms_surveys_get" in names
    assert "status_get" in names
    assert len([n for n in names if n.startswith("wiki_")]) == 6
    assert len([n for n in names if n.startswith("tracker_")]) == 13
    assert len([n for n in names if n.startswith("forms_")]) == 5
    assert len([n for n in names if n.startswith("status_")]) == 1
    assert len(names) == 25
```

- [ ] **Step 10: Add the ARCH-1 clarifying note in `ARCHITECTURE.md`**

Append to the ARCH-1 bullet (after `Use /new-endpoint to scaffold.`):
```
  *Carve-out:* `yandex/status/` and the `ycli/mcp/` server package are cross-cutting surfaces,
  not `<domain>/<resource>` dirs — the four-surface rule and the `_resource_dirs()` check
  (which scans only `tracker/wiki/forms`) do not apply to them.
```

- [ ] **Step 11: Regenerate snapshots**

Run: `uv run python -m tests.snapshots --update`
Expected: `mcp_tools.txt` gains `status_get` (sorted — it lands between `forms_*` and `tracker_*`); `cli_tree.txt` is unchanged (`auth`/`auth status` already present, `status_get` is MCP-only). Verify:
Run: `git diff tests/snapshots/`
Expected: only `+status_get` in `mcp_tools.txt`.

- [ ] **Step 12: Run the status tests + full gate**

Run: `uv run pytest tests/yandex/test_status.py tests/yandex/status/ tests/test_yandex_mcp.py -v`
Expected: PASS — existing CLI status tests still green (output still contains `"valid":true` ×3; the new `me` field adds keys but the asserts hold), new MCP tests green, 25 tools.
Run: `uv run ruff format --check . && uv run ruff check . && uv run lint-imports && uv run ty check && uv run pytest`
Expected: all green.

- [ ] **Step 13: Commit**

```bash
git add -A
git commit -m "feat: status package with native me + read-only status_get MCP tool

Explodes yandex/status.py into a package; drops ServiceProbe and the per-service
identity lambdas — each ServiceAuthStatus now carries the bare native me model.
Adds the status_get MCP tool (namespace status, read-only). ARCH-1 carve-out note.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Pagination generics + fold `collect_single_page` (W-D)

Add PEP 695 generics over (page `P`, item `T`) and a wrapped-result type, and fold the module-level `collect_single_page` into `SinglePageStrategy` as a classmethod. Behavior is unchanged; the dict-driven tests must stay valid, so the strategies stay generic over the page type via the injected callables (NOT a structural protocol requiring page attributes).

**Files:**
- Modify: `src/ycli/yandex/pagination.py`
- Modify call sites: `src/ycli/yandex/forms/surveys/client.py`, `src/ycli/yandex/wiki/attachments/client.py`, `src/ycli/yandex/wiki/comments/client.py`
- Modify: `tests/yandex/test_pagination.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `PaginationStrategy[P, T]` (generic ABC, `collect(...) -> list[T]`); `SinglePageStrategy.collect_wrapped(page_fn, *, extract, wrap, limit) -> R` (classmethod replacing the free `collect_single_page`). `CursorStrategy[P, T]`, `NextUrlStrategy[P, T]` unchanged in behavior.

- [ ] **Step 1: Update the pagination test for the folded API**

In `tests/yandex/test_pagination.py`:
- Change the import (drop `collect_single_page`):
```python
from ycli.yandex.pagination import (
    CursorStrategy,
    NextUrlStrategy,
    SinglePageStrategy,
)
```
- Replace `test_collect_single_page_extracts_wraps_and_bounds` with:
```python
def test_single_page_collect_wrapped_extracts_wraps_and_bounds():
    pages = {"a": [1, 2, 3]}
    out = SinglePageStrategy.collect_wrapped(
        lambda cursor: pages, extract=lambda p: p["a"], wrap=list, limit=2
    )
    assert out == [1, 2]
```
(All other tests are unchanged — they drive the strategies with plain `dict` pages, which the generic-over-`P` callables still accept.)

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/test_pagination.py -v`
Expected: FAIL — `SinglePageStrategy.collect_wrapped` does not exist yet; `collect_single_page` import removed.

- [ ] **Step 3: Rewrite `src/ycli/yandex/pagination.py`**

```python
"""Pagination strategies — drain an API's page mechanics into a bounded flat list.

Each strategy owns ONE cursor mechanic and accepts injected page-access callables, so the
public client method never exposes a cursor: it picks a strategy, says how to read a page,
and gets back a list capped at ``limit`` (``None`` = uncapped). Pure — no HTTP here.

Generic over the page type ``P`` (whatever ``fetch_page`` returns — a pydantic model in
production, a plain ``dict`` in tests) and the item type ``T``. The injected callables do
all structural access, so no page Protocol is imposed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class PaginationStrategy[P, T](ABC):
    @abstractmethod
    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        """Accumulate items by driving ``fetch_page`` until exhausted or ``limit`` reached."""


class SinglePageStrategy[P, T](PaginationStrategy[P, T]):
    def __init__(self, *, extract: Callable[[P], list[T]]) -> None:
        self._extract = extract

    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        items = list(self._extract(fetch_page(None)))
        return items if limit is None else items[:limit]

    @classmethod
    def collect_wrapped[R](
        cls,
        page_fn: Callable[[str | None], P],
        *,
        extract: Callable[[P], list[T]],
        wrap: Callable[[list[T]], R],
        limit: int | None = None,
    ) -> R:
        """Single-page envelope -> bounded, wrapped flat collection (the wiki/forms list shape)."""
        return wrap(cls(extract=extract).collect(page_fn, limit))


class CursorStrategy[P, T](PaginationStrategy[P, T]):
    def __init__(
        self, *, extract: Callable[[P], list[T]], next_of: Callable[[P], str | None]
    ) -> None:
        self._extract = extract
        self._next_of = next_of

    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        items: list[T] = []
        cursor: str | None = None
        while True:
            page = fetch_page(cursor)
            items.extend(self._extract(page))
            if limit is not None and len(items) >= limit:
                return items[:limit]
            cursor = self._next_of(page)
            if cursor is None:
                return items


class NextUrlStrategy[P, T](PaginationStrategy[P, T]):
    """HATEOAS: the first page comes from ``fetch_page``; subsequent ones from ``fetch_url``."""

    def __init__(
        self,
        *,
        extract: Callable[[P], list[T]],
        next_url_of: Callable[[P], str | None],
        fetch_url: Callable[[str], P],
    ) -> None:
        self._extract = extract
        self._next_url_of = next_url_of
        self._fetch_url = fetch_url

    def collect(self, fetch_page: Callable[[str | None], P], limit: int | None) -> list[T]:
        page = fetch_page(None)
        items: list[T] = list(self._extract(page))
        seen: set[str] = set()
        url = self._next_url_of(page)
        while url is not None and url not in seen:
            if limit is not None and len(items) >= limit:
                break
            seen.add(url)
            page = self._fetch_url(url)
            items.extend(self._extract(page))
            url = self._next_url_of(page)
        return items if limit is None else items[:limit]
```

Behavioral note: `CursorStrategy` previously stopped on `if not cursor` (falsy → also empty string); the new `if cursor is None` matches the API contract (`next_cursor` is `null` when exhausted, per `DescendantsResponse`) and the existing test (`next_cursor: None`). `NextUrlStrategy` previously stopped on `while url and ...`; `while url is not None and ...` is equivalent for the `str | None` shape the call site produces. The existing tests pass a dict whose `next_url_of` returns `None` at the end, so both stay green.

- [ ] **Step 4: Update call site — surveys** (`src/ycli/yandex/forms/surveys/client.py`)

Old import:
```python
from ycli.yandex.pagination import collect_single_page
```
New:
```python
from ycli.yandex.pagination import SinglePageStrategy
```
Old body of `list`:
```python
        return collect_single_page(
            lambda cursor: self._list_page(),
            extract=lambda page: page.result,
            wrap=SurveyList,
            limit=limit,
        )
```
New:
```python
        return SinglePageStrategy.collect_wrapped(
            lambda cursor: self._list_page(),
            extract=lambda page: page.result,
            wrap=SurveyList,
            limit=limit,
        )
```

- [ ] **Step 5: Update call site — attachments** (`src/ycli/yandex/wiki/attachments/client.py`)

Old import `from ycli.yandex.pagination import collect_single_page` → `from ycli.yandex.pagination import SinglePageStrategy`. Old body:
```python
        return collect_single_page(
            lambda cursor: self._list_page(page_id, page_size=100),
            extract=lambda page: page.results,
            wrap=AttachmentList,
            limit=limit,
        )
```
New:
```python
        return SinglePageStrategy.collect_wrapped(
            lambda cursor: self._list_page(page_id, page_size=100),
            extract=lambda page: page.results,
            wrap=AttachmentList,
            limit=limit,
        )
```

- [ ] **Step 6: Update call site — comments** (`src/ycli/yandex/wiki/comments/client.py`)

Identical transform to Step 5 (import + `collect_single_page(...)` → `SinglePageStrategy.collect_wrapped(...)`), with `wrap=CommentList`.

- [ ] **Step 7: Run pagination + the three resource tests**

Run: `uv run pytest tests/yandex/test_pagination.py tests/yandex/forms/surveys tests/yandex/wiki/attachments tests/yandex/wiki/comments tests/yandex/wiki/pages tests/yandex/forms/answers -v`
Expected: PASS — `wiki/pages` (CursorStrategy) and `forms/answers` (NextUrlStrategy) unchanged at the call sites and still green.

- [ ] **Step 8: Full gate**

Run: `uv run ruff format --check . && uv run ruff check . && uv run lint-imports && uv run ty check && uv run pytest`
Expected: all green. `ty check` is the load-bearing check here — the generics must resolve at all five call sites with no new `ty: ignore` (and `unused-ignore-comment = warn` + `error-on-warning = true` means no stale ignores).

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "refactor: type pagination strategies with PEP 695 generics

Strategies are generic over page type P and item T; collect returns list[T].
Folds the free collect_single_page into SinglePageStrategy.collect_wrapped.
Cursor/url termination uses 'is None' to match the null-cursor API contract.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Docstrings for the empty `__init__.py` files (W-E)

The four empty `__init__.py` exist for ARCH-1 but carry no docstring. Give them one (do NOT delete them). The `import yaml` smell from the spec was resolved in Task 2 (its only user, `test_full_renders_raw_dict_as_yaml`, was deleted).

**Files:**
- Modify: `src/ycli/yandex/__init__.py`, `src/ycli/yandex/wiki/attachments/__init__.py`, `src/ycli/yandex/wiki/comments/__init__.py`, `src/ycli/yandex/wiki/pages/__init__.py`

- [ ] **Step 1: Add docstrings** (one module-docstring line each, matching the repo style `"""<Domain> /<path> resource package."""`)

`src/ycli/yandex/__init__.py`:
```python
"""Yandex 360 SDK — per-domain clients (tracker, wiki, forms) plus shared model/MCP bases."""
```
`src/ycli/yandex/wiki/attachments/__init__.py`:
```python
"""Wiki /pages/{id}/attachments resource package."""
```
`src/ycli/yandex/wiki/comments/__init__.py`:
```python
"""Wiki /pages/{id}/comments resource package."""
```
`src/ycli/yandex/wiki/pages/__init__.py`:
```python
"""Wiki /pages resource package."""
```

- [ ] **Step 2: Full gate**

Run: `uv run ruff format --check . && uv run ruff check . && uv run ty check && uv run pytest`
Expected: all green (docstrings don't change behavior or coverage).

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "docs: add module docstrings to the four empty __init__.py files

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Reproducible demo output (W-G)

Replace the hand-typed `cat <<OUT` data branches in `docs/demo/bin/ycli` with real CLI output rendered from committed fixtures via in-process `responses`; show the real MCP tool list from `ycli mcp methods`.

**Files:**
- Create: `docs/demo/fixtures/tracker-issue.json`, `docs/demo/fixtures/wiki-page.json`
- Create: `docs/demo/render.py`
- Modify: `docs/demo/bin/ycli` (shim)
- Modify: `docs/demo/demo.tape`
- Create: `tests/test_demo_render.py`

**Interfaces:**
- Consumes: `ycli.cli.app` (in-process via `typer.testing.CliRunner`), the existing API base URLs (`https://api.tracker.yandex.net/v3`, `https://api.wiki.yandex.net/v1`).
- Produces: `docs/demo/render.py <argv...>` → prints real CLI output for the fixture; exit 0.

- [ ] **Step 1: Write the render test (TDD)**

Create `tests/test_demo_render.py`:
```python
"""The demo render harness emits real CLI output from committed fixtures (leak-free)."""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RENDER = REPO / "docs" / "demo" / "render.py"

pytestmark = pytest.mark.integration


def _run(args):
    return subprocess.run(
        [sys.executable, str(RENDER), *args],
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def test_render_tracker_issue_get_emits_fixture_key():
    proc = _run(["tracker", "issues", "get", "TRACKER-1"])
    assert proc.returncode == 0, proc.stderr
    assert "TRACKER-1" in proc.stdout


def test_render_wiki_page_get_emits_fixture_title():
    proc = _run(["wiki", "pages", "get", "onboarding"])
    assert proc.returncode == 0, proc.stderr
    assert "onboarding" in proc.stdout
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_demo_render.py -v`
Expected: FAIL — `docs/demo/render.py` does not exist.

- [ ] **Step 3: Create the fixtures**

`docs/demo/fixtures/tracker-issue.json` (fake, leak-free — fields the `Issue` model renders):
```json
{
  "key": "TRACKER-1",
  "summary": "Set up project scaffolding",
  "status": {"key": "inProgress", "display": "In Progress"},
  "assignee": {"display": "Alice"},
  "priority": {"key": "normal", "display": "Normal"}
}
```
`docs/demo/fixtures/wiki-page.json` (fields the wiki `pages get` model renders — match the real `PageDetails` shape; the implementer confirms keys against `src/ycli/yandex/wiki/pages/models.py`):
```json
{
  "slug": "onboarding",
  "title": "Team Onboarding Guide",
  "author": {"display": "Bob"},
  "revision": 7
}
```

- [ ] **Step 4: Create `docs/demo/render.py`**

```python
"""Render real `ycli` CLI output from a committed fixture — the demo's leak-free data source.

Used only by docs/demo/bin/ycli (the vhs shim). Stubs the matching API endpoint with
`responses`, sets dummy creds, and invokes the real Typer app in-process so the printed
output is genuine rendering of committed data — deterministic, offline, no real org data.

    python docs/demo/render.py tracker issues get TRACKER-1
    python docs/demo/render.py wiki pages get onboarding
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import responses
from typer.testing import CliRunner

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
TRACKER = "https://api.tracker.yandex.net/v3"
WIKI = "https://api.wiki.yandex.net/v1"

# Map a demo command (argv tuple) to (HTTP method, URL, fixture file).
ROUTES = {
    ("tracker", "issues", "get", "TRACKER-1"): (
        responses.GET,
        f"{TRACKER}/issues/TRACKER-1",
        "tracker-issue.json",
    ),
    ("wiki", "pages", "get", "onboarding"): (
        responses.GET,
        f"{WIKI}/pages/onboarding",
        "wiki-page.json",
    ),
}


def main(argv: list[str]) -> int:
    route = ROUTES.get(tuple(argv))
    if route is None:
        print(f"demo render: unknown command {argv}", file=sys.stderr)
        return 2
    method, url, fixture = route
    body = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))

    from ycli import cli

    runner = CliRunner()
    with responses.RequestsMock() as rsps:
        rsps.add(method, url, json=body, status=200)
        # Dummy creds satisfy Credentials(); responses intercepts the call (no real network).
        env = {"YANDEX_ID_OAUTH_TOKEN": "demo", "YANDEX_ID_ORGANIZATION_ID": "demo"}
        result = runner.invoke(cli.app, ["--format", "pretty", *argv], env=env)
    sys.stdout.write(result.stdout)
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

Implementer note: confirm the wiki `pages get` URL path (`/pages/{slug}` vs a query param) against `src/ycli/yandex/wiki/pages/client.py`; adjust the `ROUTES` URL (and the `--format pretty` choice if pretty needs a TTY — fall back to `json` if `pretty` renders empty under `CliRunner`). The test in Step 1 is the gate.

- [ ] **Step 5: Run the render test**

Run: `uv run pytest tests/test_demo_render.py -v`
Expected: PASS — both commands emit the fixture's key field. If `--format pretty` yields empty output under `CliRunner`, switch the `render.py` invoke to `["--format", "json", *argv]` and re-run.

- [ ] **Step 6: Update the shim `docs/demo/bin/ycli`**

```bash
#!/usr/bin/env bash
# Demo shim used ONLY by docs/demo/demo.tape. Real `--help` and a real `mcp methods`
# tool list; the data commands render committed fixtures through the REAL ycli via
# docs/demo/render.py (no network, no credentials). Keeps the GIF reproducible and
# leak-free. Not installed; not on a user's PATH.
case "$*" in
  "--help"|"")
    exec uv run ycli --help ;;
  "tracker issues get TRACKER-1"|"wiki pages get onboarding")
    exec uv run python docs/demo/render.py "$@" ;;
  "mcp methods")
    exec uv run --extra mcp ycli mcp methods ;;
  *)
    exec uv run ycli "$@" ;;
esac
```

- [ ] **Step 7: Update `docs/demo/demo.tape`**

Replace the `mcp start` step (which faked a tool list) with the real `mcp methods`, and keep the two fixture-rendered data commands. Change:
```
# Read-only MCP server banner with real tool names.
Type "ycli mcp start" Sleep 500ms Enter
Sleep 3s
```
to:
```
# Real read-only MCP tool list (no creds, no network).
Type "ycli mcp methods" Sleep 500ms Enter
Sleep 3s
```
Also bump `Set Height 720` to `Set Height 900` (the real list is ~24 lines) so the tool list is not clipped. Update the tape header comment block: the data commands now render committed fixtures via `docs/demo/render.py`, and `mcp methods` needs the `mcp` extra at regeneration time.

- [ ] **Step 8: Full gate**

Run: `uv run ruff format --check . && uv run ruff check . && uv run lint-imports && uv run ty check && uv run pytest`
Expected: all green. (`render.py` lives under `docs/`, not `src/ycli`, so it is outside the coverage source — the `test_demo_render.py` subprocess test guards it from rot without affecting the 100% gate.)

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "build: render demo output from committed fixtures, not hand-typed text

docs/demo/render.py runs the real ycli in-process against committed JSON fixtures via
responses (deterministic, leak-free, offline); the demo's MCP tool list now comes from
the real 'ycli mcp methods' instead of a baked, drift-prone list.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage:**
- W-A (RawMapping/full) → Task 2 ✓
- W-B (status package + native me + status_get) → Task 3 ✓
- W-C (ycli/mcp package) → Task 1 ✓ (with the fastmcp-free `__init__` refinement)
- W-D (pagination generics + Envelope) → Task 4 ✓ (Envelope refined to generic `P`/`T` params, not a structural protocol, to keep dict-driven tests valid — documented in the task)
- W-E (smell sweep) → Task 5 ✓ (the `import yaml` item is obviated by Task 2; only the four docstrings remain)
- W-F (ARCH docs + snapshots) → folded into Tasks 1/2/3 (ARCH-3 in T1, ARCH-4 + READ_VERBS + resources §4 in T2, ARCH-1 note in T3; snapshots regenerated in T2/T3) ✓
- W-G (demo) → Task 6 ✓

**2. Placeholder scan:** No TBD/TODO. Two explicit implementer confirmations remain (wiki page URL shape in T6 Step 4; `--format pretty` vs `json` under CliRunner in T6 Step 5) — both are guarded by the Step 1 test, not open-ended directives. The `me` union fallback to `dict` (T3) is a stated contingency, not a placeholder.

**3. Type consistency:** `StatusReporter(me_clients).report(configured=, organization_id=)` is used identically in `status/cli.py` and `status/mcp.py`. `ServiceAuthStatus(service, valid, me, detail)` and `AuthReport(configured, organization_id, services)` match across T3. `SinglePageStrategy.collect_wrapped(page_fn, *, extract, wrap, limit)` matches the three call sites and the test in T4. `from ycli.mcp import mcp, main` (lazy) is consumed by `_surface.py`, `test_architecture.py`, `test_yandex_mcp.py`, and `mcp/cli.py` — all unchanged.

**Cross-task ordering:** T1 (mcp package) precedes T3 (mounts status in `mcp/server.py`). T2 sets the MCP total to 24; T3 restores it to 25 — both edit `test_yandex_mcp.py` sequentially. No task depends on a later task.
