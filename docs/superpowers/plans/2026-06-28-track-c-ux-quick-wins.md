# Track C — UX Quick-Wins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A batch of user- and agent-facing quality wins across the CLI, MCP server, and SDK — typed errors, richer MCP metadata, shell completion, an auth probe, did-you-mean hints, and clickable Tracker keys.

**Architecture:** Seven mostly-independent tasks. Foundational first (typed errors → metadata → completion → the `me` resource → auth status → did-you-mean → key links). Every change respects the six ARCH invariants and ships with a TDD test.

**Tech Stack:** Python 3.12+, Typer (CLI), FastMCP (MCP), uplink+requests (SDK transport), rich (output), pydantic (models), stdlib `difflib`. Tests: pytest + `responses` (HTTP stubbing).

## Global Constraints

- No hand-edited `pyproject.toml` dependency lists (this track needs no new deps — `difflib` is stdlib).
- ARCH invariants stay green: `uv run lint-imports`; `uv run pytest tests/test_architecture.py tests/test_snapshots.py -q --no-cov`. HTTP only in `client.py`; no `requests`/`uplink` in `**/cli.py`/`**/mcp.py`/`**/models.py`; `fastmcp` only in `**/mcp.py`; CLI output only via `ycli.output.render`; MCP tools read-only (verb in the allow-list `{get,list,count,full,search,descendants,meta}` + `readOnlyHint`); every resource dir has all five canonical files; `model_dump_json` only in `output.py`.
- 100% coverage stays green (`uv run pytest`). Every new branch ships with a test.
- Conventional Commits per task; the branch squash-merges as **`feat:`** → **v0.5.0**.
- Work on branch `feat/track-c-ux` (already created with the spec). Never write a CI-skip token (`[skip ci]`/`[ci skip]`/`[no ci]`/`skip-checks: true`) in any commit message.
- Snapshot updates are intentional: when the CLI tree or MCP tool list changes, run `uv run python -m tests.snapshots --update` and confirm the diff is exactly the expected additions.
- The MCP server stays read-only — no write tool, ever.

---

### Task 1: C6 — typed SDK exception hierarchy

**Files:**
- Create: `src/ycli/yandex/errors.py`
- Create: `tests/yandex/test_errors.py`
- Modify: `src/ycli/yandex/transport.py` (install a response hook that raises typed errors)
- Modify: `src/ycli/cli.py` (wrap `app()` so an uncaught `YandexError` prints one line, not a traceback)
- Modify: `src/ycli/yandex/forms/answers/client.py` (drop the now-redundant manual `raise_for_status`)

**Interfaces:**
- Produces: `ycli.yandex.errors.YandexError(message, *, status=None, url=None)` with subclasses `YandexAuthError` (401/403), `YandexNotFoundError` (404), `YandexRateLimitError` (429), `YandexServerError` (5xx), `YandexClientError` (other 4xx). The transport raises these on any non-2xx response, through uplink (verified: uplink calls `session.request`, which dispatches the hook).

- [ ] **Step 1: Write the failing test**

Create `tests/yandex/test_errors.py`:

```python
"""Typed SDK errors: the transport raises the right class on each non-2xx status."""
from __future__ import annotations

import pytest
import responses

from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
)
from ycli.yandex.transport import Transport


def _get(status: int):
    """Fire one GET through a transport session at a stubbed URL of the given status."""
    url = "https://api.tracker.yandex.net/v3/probe"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=status, json={"errorMessages": ["boom"]})
        session = Transport.session(token="t", org_id="o")
        return session.get(url)


@pytest.mark.parametrize(
    ("status", "exc"),
    [
        (401, YandexAuthError),
        (403, YandexAuthError),
        (404, YandexNotFoundError),
        (429, YandexRateLimitError),
        (503, YandexServerError),
        (418, YandexClientError),
    ],
)
def test_status_maps_to_typed_error(status, exc):
    with pytest.raises(exc) as info:
        _get(status)
    assert isinstance(info.value, YandexError)
    assert info.value.status == status
    assert str(status) in str(info.value)


def test_success_does_not_raise():
    url = "https://api.tracker.yandex.net/v3/ok"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=200, json={"ok": True})
        session = Transport.session(token="t", org_id="o")
        assert session.get(url).json() == {"ok": True}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/yandex/test_errors.py -q --no-cov`
Expected: FAIL — `ycli.yandex.errors` does not exist.

- [ ] **Step 3: Create the exception module**

Create `src/ycli/yandex/errors.py`:

```python
"""Typed exceptions for Yandex API failures — pure classes, no HTTP imports.

Kept free of ``requests``/``uplink`` so cli/mcp may import it under ARCH-2. The
transport (``transport.py``) maps a non-2xx response to one of these and raises it.
"""
from __future__ import annotations


class YandexError(Exception):
    """Base for every Yandex API error. Carries the HTTP status and request URL."""

    def __init__(self, message: str, *, status: int | None = None, url: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.url = url


class YandexAuthError(YandexError):
    """401/403 — missing, invalid, or insufficient credentials."""


class YandexNotFoundError(YandexError):
    """404 — the resource does not exist (or is not visible to this token)."""


class YandexRateLimitError(YandexError):
    """429 — rate limited (after the transport's retries were exhausted)."""


class YandexServerError(YandexError):
    """5xx — upstream Yandex error (after retries were exhausted)."""


class YandexClientError(YandexError):
    """Other 4xx — a client-side problem not covered by the specific classes."""
```

- [ ] **Step 4: Install the transport response hook**

In `src/ycli/yandex/transport.py`, add the import and a module-level hook function, and register it in `session()`. Add after the existing imports:

```python
from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
)
```

Add this module-level function (above the `Transport` class):

```python
def _raise_typed(response: Response, *args: Any, **kwargs: Any) -> Response:
    """requests ``response`` hook: turn a final non-2xx into a typed ``YandexError``.

    Runs after urllib3 retries (Retry has ``raise_on_status=False``), so only the
    final response reaches here. uplink calls ``session.request``, which dispatches
    this hook, so every SDK call is covered.
    """
    code = response.status_code
    if code < 400:
        return response
    snippet = response.text[:300].replace("\n", " ").strip()
    msg = f"{code} {response.reason} for {response.request.method} {response.url}: {snippet}"
    url = response.url
    if code in (401, 403):
        raise YandexAuthError(msg, status=code, url=url)
    if code == 404:
        raise YandexNotFoundError(msg, status=code, url=url)
    if code == 429:
        raise YandexRateLimitError(msg, status=code, url=url)
    if code >= 500:
        raise YandexServerError(msg, status=code, url=url)
    raise YandexClientError(msg, status=code, url=url)
```

In `Transport.session()`, register the hook on the session right after the headers are set (before mounting adapters):

```python
        session.hooks["response"].append(_raise_typed)
```

- [ ] **Step 5: Run the error tests**

Run: `uv run pytest tests/yandex/test_errors.py -q --no-cov`
Expected: PASS (7 cases).

- [ ] **Step 6: Drop the now-redundant manual raise_for_status**

In `src/ycli/yandex/forms/answers/client.py`, remove the line `resp.raise_for_status()` (line ~53) — the transport hook now raises before the caller sees the response. Read the surrounding method first; if removing it leaves an unused `resp` variable or an empty block, simplify minimally so the method still returns its value. Run `uv run pytest tests/ -q --no-cov -k answers` to confirm the answers client still passes.

- [ ] **Step 7: Friendly CLI error (no traceback)**

In `src/ycli/cli.py`, import the error and wrap the entry point. Change `main()`:

```python
def main() -> None:  # pragma: no cover
    """Console-script entry point (``ycli`` / ``yandex-cli``)."""
    from ycli.yandex.errors import YandexError

    try:
        app()
    except YandexError as exc:
        import typer

        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc
```

(The import is inside `main()` to keep module import light; `main()` is `# pragma: no cover`.)

- [ ] **Step 8: Full suite + guards**

Run: `uv run pytest -q` (expected: PASS, 100%) and `uv run lint-imports` (expected: 2 kept, 0 broken — `errors.py` is pure so ARCH-2 holds).

- [ ] **Step 9: Commit**

```bash
git add src/ycli/yandex/errors.py tests/yandex/test_errors.py src/ycli/yandex/transport.py src/ycli/cli.py src/ycli/yandex/forms/answers/client.py
git commit -m "feat: raise typed SDK errors (YandexAuthError/NotFound/RateLimit/...) at the transport boundary"
```

---

### Task 2: MCP metadata — annotations, server instructions, per-tool titles

**Files:**
- Modify: `src/ycli/yandex/tracker/_deps.py`, `src/ycli/yandex/wiki/_deps.py`, `src/ycli/yandex/forms/_deps.py` (extend `RO`)
- Modify: `src/ycli/mcp.py` (root server `instructions`)
- Modify: `src/ycli/yandex/tracker/mcp.py`, `src/ycli/yandex/wiki/mcp.py`, `src/ycli/yandex/forms/mcp.py` (domain `instructions`)
- Modify: every resource `mcp.py` under `src/ycli/yandex/**` (add a per-tool `title`)
- Create: `tests/test_mcp_metadata.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: every MCP tool exposes `readOnlyHint=idempotentHint=openWorldHint=True` and a non-empty `title`; the root + three domain servers expose a non-empty `instructions`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_mcp_metadata.py`:

```python
"""Every MCP tool carries the read/idempotent/open-world hints + a title; servers have instructions."""
from __future__ import annotations

import asyncio

from fastmcp import Client

from ycli.mcp import mcp as root_mcp
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp


def _tools():
    async def go():
        async with Client(root_mcp) as client:
            return await client.list_tools()
    return asyncio.run(go())


def test_every_tool_has_hints_and_title():
    tools = _tools()
    assert tools
    for tool in tools:
        ann = tool.annotations
        assert ann is not None, tool.name
        assert ann.readOnlyHint is True, tool.name
        assert ann.idempotentHint is True, tool.name
        assert ann.openWorldHint is True, tool.name
        assert ann.title and ann.title.strip(), f"{tool.name} has no title"


def test_servers_have_instructions():
    for server in (root_mcp, tracker_mcp, wiki_mcp, forms_mcp):
        assert server.instructions and server.instructions.strip()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_mcp_metadata.py -q --no-cov`
Expected: FAIL — tools lack `idempotentHint`/`openWorldHint`/`title`; servers lack `instructions`.

- [ ] **Step 3: Extend the RO annotation dict**

In each of `src/ycli/yandex/tracker/_deps.py`, `wiki/_deps.py`, `forms/_deps.py`, change the `RO` line to:

```python
RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}
```

- [ ] **Step 4: Add server instructions**

In `src/ycli/mcp.py`, change `mcp = FastMCP("yandex")` to:

```python
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
```

In `src/ycli/yandex/tracker/mcp.py`, change `mcp = FastMCP("tracker")` to:

```python
mcp = FastMCP(
    "tracker",
    instructions=(
        "Read-only Yandex Tracker. Reference issues by key (e.g. QUEUE-123). "
        "issues_search / issues_count take a TQL query string; issues_list takes structured "
        "filters (queue/status/assignee/epic/type)."
    ),
)
```

In `src/ycli/yandex/wiki/mcp.py`, change `mcp = FastMCP("wiki")` to:

```python
mcp = FastMCP(
    "wiki",
    instructions=(
        "Read-only Yandex Wiki. Pages are addressed by their permanent slug: pages_get "
        "fetches content, pages_meta the metadata, pages_descendants the child tree."
    ),
)
```

In `src/ycli/yandex/forms/mcp.py`, change `mcp = FastMCP("forms")` to:

```python
mcp = FastMCP(
    "forms",
    instructions=(
        "Read-only Yandex Forms. Reference a survey by id: surveys_list enumerates them, "
        "questions_list / answers_list drill into one."
    ),
)
```

- [ ] **Step 5: Add a title to every tool**

For each `@mcp.tool(name="<local>", annotations=RO, tags=TAGS)` decorator, change `annotations=RO` to `annotations={**RO, "title": "<title>"}` using this map (file → local name → title):

- `tracker/issues/mcp.py`: `issues_get`→"Get Tracker issue", `issues_full`→"Get full Tracker issue (raw)", `issues_list`→"List Tracker issues", `issues_search`→"Search Tracker issues (TQL)", `issues_count`→"Count Tracker issues"
- `tracker/comments/mcp.py`: `comments_list`→"List Tracker issue comments"
- `tracker/links/mcp.py`: `links_list`→"List Tracker issue links"
- `tracker/transitions/mcp.py`: `transitions_list`→"List Tracker issue transitions"
- `tracker/worklog/mcp.py`: `worklog_list`→"List Tracker worklog"
- `tracker/changelog/mcp.py`: `changelog_list`→"List Tracker issue changelog"
- `tracker/priorities/mcp.py`: `priorities_list`→"List Tracker priorities"
- `tracker/issuetypes/mcp.py`: `issuetypes_list`→"List Tracker issue types"
- `tracker/linktypes/mcp.py`: `linktypes_list`→"List Tracker link types"
- `wiki/pages/mcp.py`: `pages_get`→"Get Wiki page", `pages_meta`→"Get Wiki page metadata", `pages_descendants`→"List Wiki page descendants"
- `wiki/comments/mcp.py`: `comments_list`→"List Wiki comments"
- `wiki/attachments/mcp.py`: `attachments_list`→"List Wiki attachments"
- `forms/me/mcp.py`: `me_get`→"Get current Forms user"
- `forms/surveys/mcp.py`: `surveys_get`→"Get Forms survey", `surveys_list`→"List Forms surveys"
- `forms/questions/mcp.py`: `questions_list`→"List Forms questions"
- `forms/answers/mcp.py`: `answers_list`→"List Forms answers"

(The Tracker `me` resource's tool gets its title in Task 4, when it is created.)

- [ ] **Step 6: Run the metadata test + full suite**

Run: `uv run pytest tests/test_mcp_metadata.py -q --no-cov` (expected PASS), then `uv run pytest -q` (expected PASS, 100%). The MCP-tool snapshot records only names, so `mcp_tools.txt` is unchanged.

- [ ] **Step 7: Commit**

```bash
git add src/ycli/yandex/*/_deps.py src/ycli/mcp.py src/ycli/yandex/*/mcp.py src/ycli/yandex/*/*/mcp.py tests/test_mcp_metadata.py
git commit -m "feat: enrich MCP metadata — idempotent/openWorld hints, server instructions, per-tool titles"
```

---

### Task 3: C1 — shell completion

**Files:**
- Modify: `src/ycli/cli.py` (remove `add_completion=False`)
- Test: existing `tests/test_snapshots.py` + a small assertion in `tests/test_yandex_cli.py`

**Interfaces:** Consumes/produces nothing for other tasks.

- [ ] **Step 1: Write the failing/guard test**

Add to `tests/test_yandex_cli.py` (a `@pytest.mark.integration` test, matching the file's style):

```python
@pytest.mark.integration
def test_completion_is_enabled():
    """Shell completion is enabled: --install-completion appears in --help."""
    from typer.testing import CliRunner

    from ycli.cli import app

    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "install-completion" in result.output
```

(If `tests/test_yandex_cli.py` does not already import `pytest`/`CliRunner`, add the imports at the top. The `--help` check is shell-independent, unlike invoking `--show-completion`.)

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_yandex_cli.py -q --no-cov -k completion_is_enabled`
Expected: FAIL — with `add_completion=False`, `--help` does not list `--install-completion`.

- [ ] **Step 3: Enable completion**

In `src/ycli/cli.py`, delete the `add_completion=False,` line from the root `typer.Typer(...)` call.

- [ ] **Step 4: Run it to verify it passes**

Run: `uv run pytest tests/test_yandex_cli.py -q --no-cov -k show_completion`
Expected: PASS.

- [ ] **Step 5: Confirm the snapshot is unchanged**

Run: `uv run pytest tests/test_snapshots.py -q --no-cov`
Expected: PASS unchanged — completion adds root *options* (`--install-completion`/`--show-completion`), not subcommands, and `cli_tree()` walks subcommands only. If (unexpectedly) the snapshot test fails, inspect the diff: only accept it if it is exactly completion-related, via `uv run python -m tests.snapshots --update`.

- [ ] **Step 6: Full suite + commit**

Run: `uv run pytest -q` (expected PASS, 100%).

```bash
git add src/ycli/cli.py tests/test_yandex_cli.py
git commit -m "feat: enable shell completion (--install-completion / --show-completion)"
```

---

### Task 4: Tracker `me` resource (auth target)

**Files:**
- Create (via generator, then fill): `src/ycli/yandex/tracker/me/{__init__,models,client,cli,mcp}.py`
- Modify: `src/ycli/yandex/tracker/client.py`, `tracker/cli.py`, `tracker/mcp.py` (register the resource)
- Create: `tests/yandex/tracker/test_me.py`
- Update: `tests/snapshots/cli_tree.txt`, `tests/snapshots/mcp_tools.txt`

**Interfaces:**
- Produces: `TrackerClient.from_env().me.get() -> Me`; CLI `ycli tracker me get`; MCP tool `tracker_me_get`. `Me` has `uid: int | None`, `login: str | None`, `display: str | None`, `email: str | None`.

> **Naming note:** the spec called this `myself`; this plan uses **`me`** to parallel the existing `forms me` resource (the closest template). The client still calls Tracker's `/v3/myself`.

- [ ] **Step 1: Scaffold via the generator**

Run: `uv run python scripts/new_endpoint.py tracker me`
Expected: prints `scaffolded .../tracker/me` and a next-steps list; creates the five canonical files with FILL markers.

- [ ] **Step 2: Write the failing test**

Create `tests/yandex/tracker/test_me.py`:

```python
"""Tracker /myself resource — client + CLI + MCP, HTTP stubbed."""
from __future__ import annotations

import asyncio

import responses
from fastmcp import Client

from ycli.mcp import mcp as root_mcp
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.me.models import Me

_URL = "https://api.tracker.yandex.net/v3/myself"
_PAYLOAD = {"uid": 42, "login": "alice", "display": "Alice A.", "email": "alice@example.com"}


def _env(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_me_client_get(monkeypatch):
    _env(monkeypatch)
    responses.add(responses.GET, _URL, json=_PAYLOAD, status=200)
    me = TrackerClient.from_env().me.get()
    assert isinstance(me, Me)
    assert me.login == "alice" and me.uid == 42


@responses.activate
def test_me_mcp_tool(monkeypatch):
    _env(monkeypatch)
    responses.add(responses.GET, _URL, json=_PAYLOAD, status=200)

    async def go():
        async with Client(root_mcp) as client:
            return await client.call_tool("tracker_me_get", {})

    result = asyncio.run(go())
    assert result.data.login == "alice"
```

- [ ] **Step 3: Run it to verify it fails**

Run: `uv run pytest tests/yandex/tracker/test_me.py -q --no-cov`
Expected: FAIL — the FILL stubs don't return a real `Me` / the tool isn't registered.

- [ ] **Step 4: Fill the five files (mirror `forms/me`)**

`src/ycli/yandex/tracker/me/__init__.py`:

```python
"""Tracker /myself resource (the authenticated user)."""
```

`src/ycli/yandex/tracker/me/models.py`:

```python
"""Pydantic model for Tracker /myself (Me)."""
from __future__ import annotations

from pydantic import BaseModel


class Me(BaseModel):
    """The authenticated Tracker user (``GET /v3/myself``) — a safe auth probe."""

    uid: int | None = None
    login: str | None = None
    display: str | None = None
    email: str | None = None
```

`src/ycli/yandex/tracker/me/client.py` (note: no `from __future__` — uplink reads annotations eagerly):

```python
"""Declarative Tracker /myself client (uplink) — transport ONLY."""
import uplink

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker.me.models import Me


class MeClient(TrackerResource):
    """Declarative HTTP for ``/myself``."""

    @uplink.timeout(30)
    @uplink.returns.json()
    @uplink.get("myself")
    def get(self) -> Me:  # ty: ignore[empty-body]
        """``GET /myself`` → the authenticated ``Me`` (a safe auth probe)."""
```

`src/ycli/yandex/tracker/me/cli.py`:

```python
"""`tracker me` commands."""
from __future__ import annotations

import typer

from ycli.output import render
from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="me", help="Tracker authenticated user.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context) -> None:
    """Print the authenticated user (a safe auth probe)."""
    render(tracker_client(ctx).me.get())
```

`src/ycli/yandex/tracker/me/mcp.py`:

```python
"""Tracker /myself FastMCP tool (reads-only) — Depends DI."""
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.me.models import Me

mcp = FastMCP("tracker-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Tracker user"}, tags=TAGS)
def get(client: TrackerClient = Depends(tracker_client)) -> Me:
    """The authenticated Yandex Tracker user (a safe auth probe)."""
    result = client.me.get()
    if result.login is None:
        raise ValueError("auth probe failed — empty user (check YANDEX_ID_OAUTH_TOKEN)")
    return result
```

- [ ] **Step 5: Register the resource**

In `src/ycli/yandex/tracker/client.py`: add `from ycli.yandex.tracker.me.client import MeClient` and, in `__init__`, `self.me = MeClient(session=session)`.

In `src/ycli/yandex/tracker/cli.py`: add `from ycli.yandex.tracker.me.cli import app as me_app` and `app.add_typer(me_app)` (place it first, mirroring `forms/cli.py`).

In `src/ycli/yandex/tracker/mcp.py`: add `from ycli.yandex.tracker.me.mcp import mcp as me_mcp` and `mcp.mount(me_mcp)`.

- [ ] **Step 6: Run the resource test**

Run: `uv run pytest tests/yandex/tracker/test_me.py -q --no-cov`
Expected: PASS (2 tests).

- [ ] **Step 7: Update the snapshots (intentional surface change)**

Run: `uv run python -m tests.snapshots --update`
Then confirm the diff adds exactly `tracker me` + `tracker me get` to `cli_tree.txt` and `tracker_me_get` to `mcp_tools.txt`:

```bash
git diff tests/snapshots/cli_tree.txt tests/snapshots/mcp_tools.txt
```

- [ ] **Step 8: Architecture + full suite**

Run: `uv run lint-imports` (2 kept/0 broken), `uv run pytest -q` (PASS, 100%, including `tests/test_architecture.py` ARCH-1 symmetry and `tests/test_mcp_metadata.py` — the new tool has hints + title).

- [ ] **Step 9: Commit**

```bash
git add src/ycli/yandex/tracker/me/ src/ycli/yandex/tracker/client.py src/ycli/yandex/tracker/cli.py src/ycli/yandex/tracker/mcp.py tests/yandex/tracker/test_me.py tests/snapshots/cli_tree.txt tests/snapshots/mcp_tools.txt
git commit -m "feat: add Tracker /myself resource (ycli tracker me / tracker_me_get)"
```

---

### Task 5: C3 — `ycli auth status`

**Files:**
- Create: `src/ycli/authcli.py`
- Modify: `src/ycli/cli.py` (mount the `auth` sub-app)
- Create: `tests/test_auth_status.py`
- Update: `tests/snapshots/cli_tree.txt` (adds `auth` + `auth status`)

**Interfaces:**
- Consumes: `TrackerClient.me.get()` (Task 4) and `YandexAuthError`/`YandexError` (Task 1).
- Produces: CLI `ycli auth status`; an `AuthStatus` pydantic model rendered via `ycli.output.render`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_auth_status.py`:

```python
"""`ycli auth status` — env check + a real /myself probe, errors caught."""
from __future__ import annotations

import responses
from typer.testing import CliRunner

from ycli.cli import app

_URL = "https://api.tracker.yandex.net/v3/myself"
_RUNNER = CliRunner()


def test_auth_status_missing_env(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    result = _RUNNER.invoke(app, ["auth", "status"])
    assert result.exit_code != 0
    assert "not configured" in result.stdout.lower() or "configured" in result.stdout.lower()


@responses.activate
def test_auth_status_valid(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, _URL, json={"login": "alice", "display": "Alice", "uid": 1}, status=200)
    result = _RUNNER.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "alice" in result.stdout


@responses.activate
def test_auth_status_invalid_token(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "bad")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, _URL, json={"errorMessages": ["unauthorized"]}, status=401)
    result = _RUNNER.invoke(app, ["auth", "status"])
    assert result.exit_code != 0
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_auth_status.py -q --no-cov`
Expected: FAIL — there is no `auth` command yet.

- [ ] **Step 3: Implement the auth command**

Create `src/ycli/authcli.py`:

```python
"""`ycli auth status` — validate credentials against Tracker /myself and report."""
from __future__ import annotations

import os

import typer
from pydantic import BaseModel

from ycli.output import render
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)


class AuthStatus(BaseModel):
    """The result of an auth probe — rendered like any other ycli result."""

    configured: bool
    org_id: str = ""
    valid: bool = False
    login: str | None = None
    display: str | None = None
    detail: str = ""


@app.command()
def status() -> None:
    """Report whether the env credentials are set and actually work."""
    token = os.environ.get("YANDEX_ID_OAUTH_TOKEN", "")
    org = os.environ.get("YANDEX_ID_ORGANIZATION_ID", "")
    if not token or not org:
        missing = ", ".join(
            name
            for name, value in (
                ("YANDEX_ID_OAUTH_TOKEN", token),
                ("YANDEX_ID_ORGANIZATION_ID", org),
            )
            if not value
        )
        render(AuthStatus(configured=False, org_id=org, detail=f"not configured — missing {missing}"))
        raise typer.Exit(1)

    try:
        me = TrackerClient.from_env().me.get()
    except YandexAuthError:
        render(AuthStatus(configured=True, org_id=org, valid=False, detail="token invalid or expired"))
        raise typer.Exit(1) from None
    except YandexError as exc:
        render(AuthStatus(configured=True, org_id=org, valid=False, detail=str(exc)))
        raise typer.Exit(1) from None

    render(AuthStatus(configured=True, org_id=org, valid=True, login=me.login, display=me.display))
```

- [ ] **Step 4: Mount it on the root CLI**

In `src/ycli/cli.py`, add `from ycli.authcli import app as auth_app` and `app.add_typer(auth_app)` (next to the domain `add_typer` calls).

- [ ] **Step 5: Run the auth tests**

Run: `uv run pytest tests/test_auth_status.py -q --no-cov`
Expected: PASS (3 tests).

- [ ] **Step 6: Update the snapshot**

Run: `uv run python -m tests.snapshots --update`; confirm the diff adds exactly `auth` + `auth status` to `cli_tree.txt`:

```bash
git diff tests/snapshots/cli_tree.txt
```

- [ ] **Step 7: Architecture + full suite**

Run: `uv run lint-imports` (2 kept/0 broken — `authcli.py` is `ycli.authcli`, outside the `yandex.**.cli` contract, and imports no `requests`/`uplink` directly), then `uv run pytest -q` (PASS, 100%).

- [ ] **Step 8: Commit**

```bash
git add src/ycli/authcli.py src/ycli/cli.py tests/test_auth_status.py tests/snapshots/cli_tree.txt
git commit -m "feat: add `ycli auth status` — validate credentials against Tracker /myself"
```

---

### Task 6: C4 — "did you mean?" for unknown subcommands

**Files:**
- Create: `src/ycli/_group.py`
- Modify: `src/ycli/cli.py` and `src/ycli/yandex/{tracker,wiki,forms}/cli.py` (use the suggesting group)
- Create: `tests/test_did_you_mean.py`

**Interfaces:**
- Produces: `ycli._group.SuggestGroup` — a `typer.core.TyperGroup` subclass that appends a "Did you mean '<x>'?" hint to the unknown-command error.

- [ ] **Step 1: Write the failing test**

Create `tests/test_did_you_mean.py`:

```python
"""Unknown subcommands suggest the closest valid one."""
from __future__ import annotations

from typer.testing import CliRunner

from ycli.cli import app

_RUNNER = CliRunner()


def test_root_typo_suggests():
    result = _RUNNER.invoke(app, ["trackr"])
    assert result.exit_code != 0
    assert "did you mean 'tracker'" in result.output.lower()


def test_domain_typo_suggests():
    result = _RUNNER.invoke(app, ["wiki", "pagez"])
    assert result.exit_code != 0
    assert "did you mean 'pages'" in result.output.lower()


def test_correct_command_unaffected():
    result = _RUNNER.invoke(app, ["--help"])
    assert result.exit_code == 0
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_did_you_mean.py -q --no-cov`
Expected: FAIL — the default error has no "Did you mean" hint.

- [ ] **Step 3: Implement the suggesting group**

Create `src/ycli/_group.py`:

```python
"""A Typer/Click group that appends a difflib 'Did you mean?' hint on unknown commands."""
from __future__ import annotations

import difflib
from typing import Any

import typer.core


class SuggestGroup(typer.core.TyperGroup):
    """On an unknown subcommand, fail with the closest valid name suggested."""

    def get_command(self, ctx: Any, cmd_name: str) -> Any:
        command = super().get_command(ctx, cmd_name)
        if command is not None:
            return command
        matches = difflib.get_close_matches(cmd_name, self.list_commands(ctx), n=1)
        hint = f" Did you mean '{matches[0]}'?" if matches else ""
        ctx.fail(f"No such command '{cmd_name}'.{hint}")
```

- [ ] **Step 4: Use it on the root + domain apps**

Add `cls=SuggestGroup` to the `typer.Typer(...)` call in each of: `src/ycli/cli.py` (root), `src/ycli/yandex/tracker/cli.py`, `src/ycli/yandex/wiki/cli.py`, `src/ycli/yandex/forms/cli.py`. Each needs `from ycli._group import SuggestGroup` at the top. Example for the root:

```python
app = typer.Typer(
    name="ycli",
    help="ycli — Yandex 360 API SDK CLI.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    cls=SuggestGroup,
)
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/test_did_you_mean.py -q --no-cov`
Expected: PASS (3 tests).

- [ ] **Step 6: Snapshot + full suite**

Run: `uv run pytest tests/test_snapshots.py -q --no-cov` (unchanged — group class doesn't alter the command tree), then `uv run pytest -q` (PASS, 100%).

- [ ] **Step 7: Commit**

```bash
git add src/ycli/_group.py src/ycli/cli.py src/ycli/yandex/tracker/cli.py src/ycli/yandex/wiki/cli.py src/ycli/yandex/forms/cli.py tests/test_did_you_mean.py
git commit -m "feat: suggest the closest command on an unknown subcommand (did-you-mean)"
```

---

### Task 7: C5 — OSC8 hyperlinks on Tracker keys (pretty, TTY-gated)

**Files:**
- Modify: `src/ycli/output.py`
- Create: `tests/test_output_links.py`

**Interfaces:** Self-contained; no new public symbol.

- [ ] **Step 1: Write the failing test**

Create `tests/test_output_links.py`:

```python
"""Tracker keys become clickable links in pretty tables on a TTY, and stay bare otherwise."""
from __future__ import annotations

import io

from pydantic import BaseModel
from rich.console import Console

from ycli.output import OutputFormat, render, set_format


class _Row(BaseModel):
    key: str
    summary: str


def _render(model, *, terminal: bool) -> str:
    set_format(OutputFormat.pretty)
    console = Console(file=io.StringIO(), force_terminal=terminal, width=200)
    render(model, console=console)
    return console.file.getvalue()


def test_key_is_linked_on_terminal():
    out = _render(_Row(key="ABC-1", summary="x"), terminal=True)
    assert "tracker.yandex.ru/ABC-1" in out  # the OSC8 target


def test_key_is_bare_when_not_terminal():
    out = _render(_Row(key="ABC-1", summary="x"), terminal=False)
    assert "tracker.yandex.ru" not in out
    assert "ABC-1" in out
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_output_links.py -q --no-cov`
Expected: FAIL — keys are rendered plain.

- [ ] **Step 3: Add the link heuristic to output.py**

In `src/ycli/output.py`, add at module level (after the imports):

```python
import re

_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")


def _key_link(value: str) -> str:
    return f"[link=https://tracker.yandex.ru/{value}]{value}[/link]"
```

Change `_cell` to accept the link context:

```python
def _cell(value: Any, *, is_key: bool = False, link: bool = False) -> str:
    """Render one cell: nested as compact JSON, ``None`` empty; a Tracker key links on a TTY."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return ""
    text = str(value)
    if link and is_key and _KEY_RE.match(text):
        return _key_link(text)
    return text
```

Thread the `link` flag from `render` down through `_prettify`. In `render`, the pretty branch becomes:

```python
    else:  # pretty
        console.print(_prettify(result.model_dump(by_alias=True, mode="json"), link=console.is_terminal))
```

Update `_prettify`, `_kv_table`, `_list_table` to pass the flag and mark the `key` field:

```python
def _prettify(data: Any, *, link: bool = False) -> Any:
    if isinstance(data, list):
        return _list_table(data, link=link)
    if isinstance(data, dict):
        return _kv_table(data, link=link)
    return str(data)


def _kv_table(data: dict[str, Any], *, link: bool = False) -> Table:
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column(style="cyan", no_wrap=True)
    table.add_column(overflow="fold")
    for key, value in data.items():
        table.add_row(str(key), _cell(value, is_key=(key == "key"), link=link))
    return table


def _list_table(items: list[Any], *, link: bool = False) -> Table:
    table = Table()
    if items and isinstance(items[0], dict):
        columns = list(items[0].keys())
        for column in columns:
            table.add_column(str(column), style="cyan", overflow="fold")
        for item in items:
            table.add_row(*[_cell(item.get(column), is_key=(column == "key"), link=link) for column in columns])
    else:
        table.add_column("value", overflow="fold")
        for item in items:
            table.add_row(_cell(item, link=link))
    return table
```

- [ ] **Step 4: Run the link tests**

Run: `uv run pytest tests/test_output_links.py -q --no-cov`
Expected: PASS (2 tests).

- [ ] **Step 5: Guard existing output tests + ARCH-4**

Run: `uv run pytest tests/test_output.py -q --no-cov` (the existing renderer tests must still pass — JSON/YAML/pretty unaffected for non-key fields). Confirm `model_dump_json` still appears only in `output.py` (ARCH-4): `uv run pytest tests/test_architecture.py -q --no-cov`.

- [ ] **Step 6: Full suite + commit**

Run: `uv run pytest -q` (PASS, 100%).

```bash
git add src/ycli/output.py tests/test_output_links.py
git commit -m "feat: link Tracker issue keys in pretty tables on a TTY (OSC8)"
```

---

## Final verification (after all tasks)

- [ ] Full suite: `uv run pytest -q` → PASS, 100%.
- [ ] Architecture: `uv run lint-imports` (2 kept/0 broken); `uv run pytest tests/test_architecture.py tests/test_snapshots.py -q --no-cov` → PASS (snapshots reflect only `tracker me`/`tracker_me_get` + `auth status`).
- [ ] Secret scan: `uv run pre-commit run gitleaks --all-files` → Passed.
- [ ] Then: PR → review → merge as `feat:` → verify **v0.5.0** on PyPI → post-release `uv lock` + `build:` commit (the lock-drift chore).

## Spec coverage map

- C6 → Task 1. Metadata → Task 2. C1 → Task 3. `me` resource → Task 4. C3 `auth status` → Task 5. C4 → Task 6. C5 → Task 7.
- Deviation from spec: the validation resource is named `me` (not `myself`), to parallel `forms me`.
