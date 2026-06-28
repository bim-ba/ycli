# Round-2 Architecture Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor ycli's internals to raw-argument dependency-injected clients, a single `Serializer` service, a typed `AppContext`, and bounded auto-pagination — and re-encode the architecture invariants — landing as `feat:` → v0.7.0.

**Architecture:** Clients take raw credential primitives (`oauth_token`/`organization_id` + tunables), never settings objects or the env. The env is read once at two composition roots: the CLI `AppContext` (on `ctx.obj`) and the MCP `lifespan`. Serialization is a stateless `Serializer.serialize(model, strategy, console)` service; models stay plain pydantic (`APIModel` base). List endpoints that paginate drain cursors internally and return flat `RootModel` collections bounded by `YCLI_MAX_ITEMS`.

**Tech Stack:** Python ≥3.12, uv, uplink+requests (sync HTTP), pydantic + pydantic-settings, typer (CLI), fastmcp 3.x (read-only MCP), rich, loguru. Tests: pytest + `responses` (HTTP stubbed, no live network), `asyncio_mode = "auto"`.

## Global Constraints

- **Full, self-documenting names** — no abbreviations (`timeout_seconds` not `timeout_s`). New env var is exactly `YCLI_MAX_ITEMS`.
- **No hand-edited dependency lists** — `uv add` only (this track needs no new runtime deps).
- **100% coverage stays green** — `uv run pytest` enforces `--cov-fail-under=100`; every new branch ships with a test.
- **Credentials only from the env** at a composition root — never hardcode `YANDEX_ID_OAUTH_TOKEN` / `YANDEX_ID_ORGANIZATION_ID`; the single credentials entry is the `oauth_token` + `organization_id` constructor arguments. A pre-authenticated `session` (one already carrying auth headers) is **rejected** by design — an injected `session` is a bare transport the client authenticates itself.
- **MCP server stays read-only** (ARCH-3) — no write tools; no `fastmcp` import outside `mcp.py`.
- **Conventional Commits**; the branch squash-merges as `feat:` → v0.7.0. Never write a CI-skip token (`[skip ci]` / `[ci skip]` / `[no ci]` / `[skip actions]` / `[actions skip]`) or a `skip-checks` trailer in any commit/merge message.
- **Snapshots are intentional (ARCH-6)** — regenerate `tests/snapshots/` only when a task deliberately changes the CLI tree, and treat the diff as reviewed. Commit messages end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **Post-release chore:** after v0.7.0 publishes, run `uv lock` + a `build:` commit (PSR bumps `pyproject.toml` but not `uv.lock`).

## Spec deviations (deliberate, flagged for the reviewer)

These refine the spec's sequencing after reading the real code; each is defensible:

1. **`output.py` already has the strategy scaffold** (`SerializationStrategy` ABC + `Json/Yaml/Pretty/AutoStrategy` + `_STRATEGIES` dict + `render()`), added in v0.6.0. This plan *evolves* it (adds `Serializer`, `from_format`, folds helpers in) rather than building from scratch.
2. **`render()` is kept as a thin shim through Phase 1–2** so call sites are rewritten exactly once (in the Phase 2 CLI sweep), not twice. It is deleted at the end of Phase 2.
3. **No separate wiki `_models.py`** — the spec proposed one to hold a wiki-local lenient base, but a single global `APIModel` (in `src/ycli/models.py`) supersedes all four `_Lenient` copies, so no per-domain base module is needed.
4. **The auth probe-loop cleanup (spec item 5) is folded into the Phase 2 auth rewrite**, since `auth.py` is rewritten there anyway (dropping `from_env`) — touching it once.
5. **Pagination scope is narrower than the spec assumed.** Reality from the code: the 9 tracker list endpoints already return flat `RootModel` collections (no envelope, no cursor) — untouched. Only **5** wiki/forms endpoints carry an envelope, and only **2** actually follow a cursor:
   - `wiki/pages.descendants` — `next_cursor` (real pagination) → `CursorStrategy`.
   - `forms/answers.list_all` — `next.next_url` (real pagination, already drains) → `NextUrlStrategy`.
   - `wiki/comments.list`, `wiki/attachments.list`, `forms/surveys.list` — single-page `{results}` / `{result}` envelopes → `SinglePageStrategy` (unwrap to flat collection).
   - `forms/questions.list` returns a *nested* `{pages:[{items}]}` structure (not a flat list) → left as-is, not a pagination target.
   Only the two real paginators gain `--limit`/`--all` CLI options (snapshot change); the single-page unwraps just change their return type. This minimizes snapshot churn while honoring "RootModel for Wiki/Forms".

---

## File Structure

**New files**
- `src/ycli/models.py` — `APIModel(BaseModel)` shared lenient base (replaces all four `_Lenient` copies).
- `src/ycli/context.py` — `AppContext` (CLI composition root: output format + console + lazy clients).
- `src/ycli/yandex/pagination.py` — `PaginationStrategy` ABC + `SinglePageStrategy` / `CursorStrategy` / `NextUrlStrategy`.
- `src/ycli/yandex/tracker/_args.py` — shared `KeyArg` + the `parse_fields` helper (moved from `_clideps.py`).
- `src/ycli/yandex/forms/_args.py` — shared `SurveyIdArg`.
- `src/ycli/yandex/_mcp.py` — shared MCP annotation dict `RO` + `TAGS` factory (de-dupes the three `_deps.py` copies).

**Deleted files**
- `src/ycli/cliformat.py`, `src/ycli/yandex/tracker/_clideps.py`, `src/ycli/yandex/wiki/_clideps.py`, `src/ycli/yandex/forms/_clideps.py`, and the `FromEnvSession` mixin (from `base.py`).

**Heavily modified**
- `src/ycli/output.py` (Serializer + from_format + helpers folded in), `src/ycli/yandex/transport.py` (raw-arg + `base=`), `src/ycli/yandex/base.py` (drop FromEnvSession), the three composition-root `client.py` (raw-arg constructor), `src/ycli/cli.py` (AppContext callback), `src/ycli/mcp.py` (lifespan), the three `_deps.py` (read lifespan context), `src/ycli/yandex/auth.py` (raw creds + probe loop), `src/ycli/yandex/settings.py` (`max_items`), every `models.py` (inherit `APIModel`), every CLI `cli.py` (AppContext + Serializer), the 5 envelope list endpoints, `scripts/new_endpoint.py`, `ARCHITECTURE.md` + `tests/test_architecture.py`.

---

## PHASE 1 — Serialization core

### Task 1: `Serializer` service + `from_format` factory in `output.py`

**Files:**
- Modify: `src/ycli/output.py`
- Test: `tests/test_output.py`, `tests/test_output_strategies.py`, `tests/test_output_links.py`, `tests/test_cliformat.py`

**Interfaces:**
- Produces:
  - `class Serializer` with `@staticmethod serialize(model: BaseModel, strategy: SerializationStrategy, console: Console) -> None`.
  - `SerializationStrategy.from_format(output_format: OutputFormat) -> SerializationStrategy` classmethod.
  - `SerializationStrategy.render(self, result: BaseModel, console: Console) -> None` (the ABC method, renamed from `serialize`).
  - `render(result, *, output_format, console=None) -> None` stays as a thin shim (deleted in Task 6).
- Consumes: nothing new.

- [ ] **Step 1: Write the failing test** — add to `tests/test_output_strategies.py`:

```python
import io
from rich.console import Console
from ycli.output import OutputFormat, Serializer, SerializationStrategy, JsonStrategy, PrettyStrategy
from pydantic import BaseModel


class _M(BaseModel):
    key: str


def test_from_format_maps_each_choice():
    assert isinstance(SerializationStrategy.from_format(OutputFormat.json), JsonStrategy)
    assert isinstance(SerializationStrategy.from_format(OutputFormat.pretty), PrettyStrategy)


def test_serializer_dispatches_to_strategy_render():
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False)
    Serializer.serialize(_M(key="DE-1"), SerializationStrategy.from_format(OutputFormat.json), console)
    assert '"key":"DE-1"' in buf.getvalue().replace(" ", "")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_output_strategies.py::test_serializer_dispatches_to_strategy_render -v`
Expected: FAIL — `ImportError: cannot import name 'Serializer'`.

- [ ] **Step 3: Implement** — rewrite `src/ycli/output.py` from the `SerializationStrategy` ABC downward. Keep the module docstring, imports, `_KEY_RE`/`_key_link` (now moved into `PrettyStrategy`), `OutputFormat`. Replace lines 41–134 with:

```python
class SerializationStrategy(ABC):
    @abstractmethod
    def render(self, result: BaseModel, console: Console) -> None: ...

    @classmethod
    def from_format(cls, output_format: OutputFormat) -> "SerializationStrategy":
        """Resolve a CLI ``--format`` choice to its strategy (no module-level registry)."""
        return {
            OutputFormat.json: JsonStrategy,
            OutputFormat.yaml: YamlStrategy,
            OutputFormat.pretty: PrettyStrategy,
            OutputFormat.auto: AutoStrategy,
        }[output_format]()


class JsonStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
        text = result.model_dump_json(by_alias=True)
        if console.is_terminal:
            console.print_json(text)
        else:
            console.file.write(text + "\n")  # pristine, unwrapped JSON for pipes


class YamlStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
        data = result.model_dump(by_alias=True, mode="json")
        console.file.write(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


class PrettyStrategy(SerializationStrategy):
    _KEY_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")

    def render(self, result: BaseModel, console: Console) -> None:
        console.print(self._prettify(result.model_dump(by_alias=True, mode="json"), link=console.is_terminal))

    def _prettify(self, data: Any, *, link: bool = False) -> Any:
        if isinstance(data, list):
            return self._list_table(data, link=link)
        if isinstance(data, dict):
            return self._kv_table(data, link=link)
        return str(data)

    def _kv_table(self, data: dict[str, Any], *, link: bool = False) -> Table:
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column(style="cyan", no_wrap=True)
        table.add_column(overflow="fold")
        for key, value in data.items():
            table.add_row(str(key), self._cell(value, is_key=(key == "key"), link=link))
        return table

    def _list_table(self, items: list[Any], *, link: bool = False) -> Table:
        table = Table()
        if items and isinstance(items[0], dict):
            columns = list(items[0].keys())
            for column in columns:
                table.add_column(str(column), style="cyan", overflow="fold")
            for item in items:
                table.add_row(*[self._cell(item.get(c), is_key=(c == "key"), link=link) for c in columns])
        else:
            table.add_column("value", overflow="fold")
            for item in items:
                table.add_row(self._cell(item, link=link))
        return table

    def _cell(self, value: Any, *, is_key: bool = False, link: bool = False) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        if value is None:
            return ""
        text = str(value)
        if link and is_key and self._KEY_RE.match(text):
            return f"[link=https://tracker.yandex.ru/{text}]{text}[/link]"
        return text


class AutoStrategy(SerializationStrategy):
    def render(self, result: BaseModel, console: Console) -> None:
        (PrettyStrategy() if console.is_terminal else JsonStrategy()).render(result, console)


class Serializer:
    """The single serialization dispatch point — applies a chosen strategy to a model."""

    @staticmethod
    def serialize(model: BaseModel, strategy: SerializationStrategy, console: Console) -> None:
        strategy.render(model, console)


def render(result: BaseModel, *, output_format: OutputFormat, console: Console | None = None) -> None:
    """Compatibility shim (removed in Phase 2). Renders ``result`` in ``output_format``."""
    Serializer.serialize(result, SerializationStrategy.from_format(output_format), console or Console())
```

Then delete the now-unused module-level `_KEY_RE`, `_key_link`, `_STRATEGIES`, `_prettify`, `_kv_table`, `_list_table`, `_cell` (they are methods/attrs of `PrettyStrategy` now).

- [ ] **Step 4: Fix references in existing tests.** `tests/test_output*.py` / `tests/test_cliformat.py` may reference the moved module-level symbols (`_prettify`, `_key_link`, `_KEY_RE`, `_STRATEGIES`, or a strategy's `.serialize(...)` method). Run the suite and update each reference: module helper `_prettify(x)` → `PrettyStrategy()._prettify(x)`; `_KEY_RE` → `PrettyStrategy._KEY_RE`; strategy `.serialize(...)` → `.render(...)`. The public `render(...)` shim and `Serializer.serialize(...)` are the supported entry points.

Run: `uv run pytest tests/test_output.py tests/test_output_strategies.py tests/test_output_links.py tests/test_cliformat.py -v`
Expected: PASS (all, including the two new tests).

- [ ] **Step 5: Commit**

```bash
git add src/ycli/output.py tests/test_output*.py tests/test_cliformat.py
git commit -m "refactor(output): add Serializer service + SerializationStrategy.from_format; fold helpers into PrettyStrategy

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: `APIModel` base + sweep all models to inherit it

**Files:**
- Create: `src/ycli/models.py`
- Modify (sweep): `src/ycli/yandex/tracker/_models.py`, `src/ycli/yandex/forms/_models.py`, and every `models.py` that defines or uses a local `_Lenient` (see enumerated list below).
- Test: `tests/test_packaging.py` (add an APIModel config assertion) + the existing per-resource `test_models.py` stay green.

**Interfaces:**
- Produces: `class APIModel(BaseModel)` with `model_config = ConfigDict(extra="ignore", populate_by_name=True)`.
- Consumes: nothing.

- [ ] **Step 1: Write the failing test** — create `tests/test_models.py`:

```python
from ycli.models import APIModel


def test_apimodel_is_lenient_and_alias_friendly():
    cfg = APIModel.model_config
    assert cfg["extra"] == "ignore"
    assert cfg["populate_by_name"] is True
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ycli.models'`.

- [ ] **Step 3: Create `src/ycli/models.py`:**

```python
"""Shared pydantic base for every Yandex API model — lenient parsing only, no behavior.

Consolidates the per-domain ``_Lenient`` bases. ``extra="ignore"`` keeps unknown API
fields from raising; ``populate_by_name=True`` lets a field be set by its Python name as
well as its serialization alias. Serialization is NOT a model concern — see ``output.py``.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base for all Yandex API models: ignore unknown fields, allow name-or-alias population."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
```

- [ ] **Step 4: Sweep — replace every `_Lenient` base with `APIModel`.** Apply this transform to each file below: (a) add `from ycli.models import APIModel`; (b) delete the local `class _Lenient(...)` definition and its now-unused `BaseModel`/`ConfigDict` imports; (c) rename every `class X(_Lenient):` → `class X(APIModel):`.

Shared-base files (delete the `_Lenient` definition, keep the other classes):
- `src/ycli/yandex/tracker/_models.py` (defines `_Lenient` at line 12; also `_KeyRef`/`_IdRef`/`_DisplayRef` inherit it)
- `src/ycli/yandex/forms/_models.py` (defines `_Lenient` at line 15)

Files inheriting the tracker/forms shared `_Lenient` — change the import from `.._models import _Lenient` (or wherever) to `from ycli.models import APIModel` and rename the base in each class:
- tracker: `issues/models.py`, `issuetypes/models.py`, `priorities/models.py`, `transitions/models.py`, `links/models.py`, `linktypes/models.py`, `changelog/models.py`, `comments/models.py`, `worklog/models.py`
- forms: `me/models.py`, `answers/models.py`, `questions/models.py`, `surveys/models.py`

Wiki files with an **inline** `_Lenient` (each defines its own at line 7 — delete it, import `APIModel`):
- `wiki/pages/models.py` (classes: `PageAttributes`, `_OwnerUser`, `_Owner`, `PageDetails`, `PageRef`, `DescendantsResponse`)
- `wiki/comments/models.py` (classes: `_CommentAuthor`, `Comment`, `CommentsResponse`)
- `wiki/attachments/models.py` (classes: `Attachment`, `AttachmentsResponse`)

Note: the wiki inline `_Lenient` used `ConfigDict(extra="ignore")` only; switching to `APIModel` additionally enables `populate_by_name=True`, which is purely additive (safe). `RootModel[...]` collection classes are unchanged — they don't use `_Lenient`.

- [ ] **Step 5: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS — 100% coverage. If a model test fails on a field set by Python name, that's the `populate_by_name` addition working; no test should regress.

- [ ] **Step 6: Commit**

```bash
git add src/ycli/models.py src/ycli/yandex tests/test_models.py
git commit -m "refactor(models): consolidate four _Lenient bases into a single APIModel

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## PHASE 2 — Dependency-injection overhaul

### Task 3: `Transport.session` raw-arg + bare-`base` injection

**Files:**
- Modify: `src/ycli/yandex/transport.py`, `src/ycli/yandex/base.py` (the one caller)
- Test: `tests/yandex/test_transport.py`

**Interfaces:**
- Produces: `Transport.session(*, oauth_token: str, organization_id: str, timeout_seconds: float = 30.0, retries: int = 3, base: requests.Session | None = None) -> requests.Session`.
- Consumes: nothing new.

- [ ] **Step 1: Write the failing test** — add to `tests/yandex/test_transport.py`:

```python
import requests
from ycli.yandex.transport import Transport


def test_session_configures_a_supplied_bare_base():
    bare = requests.Session()
    out = Transport.session(oauth_token="t", organization_id="o", base=bare)
    assert out is bare  # configured in place, not replaced
    assert out.headers["Authorization"] == "OAuth t"
    assert out.headers["X-Org-Id"] == "o"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/test_transport.py::test_session_configures_a_supplied_bare_base -v`
Expected: FAIL — `TypeError: session() got an unexpected keyword argument 'oauth_token'` (or `'base'`).

- [ ] **Step 3: Implement** — in `transport.py`:
  - Delete the `ORGANIZATION_HEADER = "X-Org-Id"` constant (line 34) and inline the literal `"X-Org-Id"` at its one use in `session.headers.update`.
  - Update the docstring example to `Transport.session(oauth_token="t", organization_id="o", ...)`.
  - Rewrite the `session` classmethod signature and body head:

```python
    @classmethod
    def session(
        cls,
        *,
        oauth_token: str,
        organization_id: str,
        timeout_seconds: float = 30.0,
        retries: int = 3,
        base: requests.Session | None = None,
    ) -> requests.Session:
        if not oauth_token:
            raise ValueError("oauth_token must be a non-empty string")
        if not organization_id:
            raise ValueError("organization_id must be a non-empty string")
        session = base or requests.Session()
        session.headers.update(
            {"Authorization": f"OAuth {oauth_token}", "X-Org-Id": organization_id}
        )
        session.hooks["response"].append(_raise_typed)
        # ... retry + _TimeoutAdapter mount unchanged (uses retries / timeout_seconds) ...
```

- [ ] **Step 4: Update the caller** — in `base.py`, `FromEnvSession.from_env` (still present this task) calls `Transport.session(token=...)`; rename its kwarg `token=` → `oauth_token=`.

- [ ] **Step 5: Run transport + base tests**

Run: `uv run pytest tests/yandex/test_transport.py tests/yandex/test_base.py -v`
Expected: PASS. (If a transport test asserted on the old `token=` kwarg or `ORGANIZATION_HEADER`, update it to `oauth_token=` / the inline string.)

- [ ] **Step 6: Commit**

```bash
git add src/ycli/yandex/transport.py src/ycli/yandex/base.py tests/yandex/test_transport.py
git commit -m "refactor(transport): raw oauth_token arg + bare-session base injection; inline org header

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4 (SPIKE): verify FastMCP lifespan + mounted subserver + `get_context()`

This is a throwaway verification, **not** shipped. It de-risks Task 6 (whether a tool in a subserver mounted under a root that owns the lifespan can read `get_context().lifespan_context`, and whether an isolated subserver can be given a context via a test wrapper).

**Files:**
- Create (temporary, deleted at end of task): `scratch_spike_lifespan.py` at repo root.

- [ ] **Step 1: Write the spike**

```python
import asyncio
from contextlib import asynccontextmanager
from fastmcp import FastMCP, Client
from fastmcp.server.dependencies import Depends, get_context

leaf = FastMCP("leaf")

def provide() -> str:
    return get_context().lifespan_context["who"]

@leaf.tool(name="leaf_whoami")
def whoami(who: str = Depends(provide)) -> str:
    return who

@asynccontextmanager
async def life(server):
    yield {"who": "from-lifespan"}

root = FastMCP("root", lifespan=life)
root.mount(leaf, namespace="leaf")

async def main():
    async with Client(root) as c:
        print("MOUNTED:", (await c.call_tool("leaf_leaf_whoami", {})).data)
    # isolated subserver wrapped with a test lifespan:
    @asynccontextmanager
    async def test_life(server):
        yield {"who": "from-test"}
    wrapper = FastMCP("wrap", lifespan=test_life)
    wrapper.mount(leaf)
    async with Client(wrapper) as c:
        names = [t.name for t in await c.list_tools()]
        print("ISOLATED:", (await c.call_tool(names[0], {})).data)

asyncio.run(main())
```

- [ ] **Step 2: Run it**

Run: `uv run python scratch_spike_lifespan.py`
Expected: `MOUNTED: from-lifespan` and `ISOLATED: from-test`.

- [ ] **Step 3: Record the verified pattern** for Task 6. If `Depends(provide)` does **not** receive the context (errors), fall back to: the provider takes `ctx: Context` (`def provide(ctx: Context)`) and Task 6 tools keep `Depends(provide)` — re-run the spike with that signature to confirm before proceeding. Whichever variant prints the expected output is the one Task 6 uses.

- [ ] **Step 4: Delete the spike, no commit**

```bash
rm scratch_spike_lifespan.py
```

---

### Task 5: `AppContext` + raw-arg composition clients + CLI sweep

This is the CLI half of the DI overhaul. It rewrites the three composition-root clients to raw-arg constructors, introduces `AppContext`, rewrites every CLI call site to `AppContext` + `Serializer`, rewrites `auth.py` (with the probe loop), and deletes `cliformat.py` / the three `_clideps.py` / the `render()` shim. The three composition clients keep a **temporary** `from_env` classmethod so the MCP `_deps.py` (untouched until Task 6) stays green.

**Files:**
- Create: `src/ycli/context.py`, `src/ycli/yandex/tracker/_args.py`, `src/ycli/yandex/forms/_args.py`
- Modify: `src/ycli/yandex/tracker/client.py`, `wiki/client.py`, `forms/client.py`, `src/ycli/cli.py`, `src/ycli/yandex/auth.py`, every CLI `cli.py` under `tracker/`, `wiki/`, `forms/`, `src/ycli/output.py` (remove `render` shim)
- Delete: `src/ycli/cliformat.py`, `tracker/_clideps.py`, `wiki/_clideps.py`, `forms/_clideps.py`
- Test: `tests/test_yandex_cli.py`, `tests/yandex/test_auth.py`, every CLI `test_cli.py`, `tests/yandex/tracker/test_clideps.py`, `tests/yandex/forms/test_clideps.py`, `tests/test_cliformat.py`

**Interfaces:**
- Produces:
  - `TrackerClient(*, oauth_token: str, organization_id: str, timeout_seconds: int = 30, retries: int = 3, session: requests.Session | None = None)` (and identically `WikiClient`, `FormsClient`).
  - `AppContext` dataclass with `.output_format`, `.console` (property), `.strategy` (property), `.tracker`/`.wiki`/`.forms` (lazy properties), `@classmethod from_typer_context(ctx) -> AppContext`.
  - `tracker/_args.py`: `KeyArg` type alias + `parse_fields(items)`.
  - `forms/_args.py`: `SurveyIdArg` type alias.
- Consumes: `Transport.session` (Task 3), `Serializer`/`SerializationStrategy` (Task 1), `Credentials`/`AppConfig` (settings).

- [ ] **Step 1: Write the failing test** — add to `tests/test_yandex_cli.py`:

```python
from types import SimpleNamespace
from ycli.context import AppContext
from ycli.output import OutputFormat, PrettyStrategy


def test_appcontext_strategy_and_retrieval():
    app = AppContext(output_format=OutputFormat.pretty)
    assert app.output_format is OutputFormat.pretty
    assert isinstance(app.strategy, PrettyStrategy)
    # from_typer_context just returns ctx.obj (set by the root callback)
    assert AppContext.from_typer_context(SimpleNamespace(obj=app)) is app
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_yandex_cli.py::test_appcontext_from_typer_context_round_trips -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ycli.context'`.

- [ ] **Step 3: Rewrite the three composition clients.** Each drops `FromEnvSession`, takes raw args, builds its session via `Transport.session`, and keeps a temporary `from_env`. Example — `tracker/client.py`:

```python
"""TrackerClient — composition root over the tracker resource clients (one shared session)."""
from __future__ import annotations

import requests

from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.transport import Transport
# ... the ten resource-client imports unchanged ...


class TrackerClient:
    """Holds the per-resource tracker clients, all sharing one authed ``requests.Session``."""

    def __init__(
        self,
        *,
        oauth_token: str,
        organization_id: str,
        timeout_seconds: int = 30,
        retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        transport = Transport.session(
            oauth_token=oauth_token,
            organization_id=organization_id,
            timeout_seconds=timeout_seconds,
            retries=retries,
            base=session,
        )
        self.me = MeClient(session=transport)
        self.issues = IssuesClient(session=transport)
        # ... fan `transport` out to every remaining sub-client (same list as before) ...

    @classmethod
    def from_env(cls) -> "TrackerClient":
        """TEMPORARY shim for the MCP _deps.py — removed in Task 6."""
        credentials, config = Credentials(), AppConfig()
        return cls(
            oauth_token=credentials.oauth_token,
            organization_id=credentials.organization_id,
            timeout_seconds=int(config.timeout_seconds),
            retries=config.retries,
        )
```

Apply the same shape to `wiki/client.py` (sub-clients: `me`, `pages`, `comments`, `attachments`) and `forms/client.py` (sub-clients: `me`, `surveys`, `questions`, `answers`).

- [ ] **Step 4: Create `src/ycli/context.py`:**

```python
"""CLI composition root — reads the env once and hands raw primitives to the clients."""
from __future__ import annotations

from dataclasses import dataclass, field

import typer
from rich.console import Console

from ycli.output import OutputFormat, SerializationStrategy
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient


@dataclass
class AppContext:
    """Stored on ``ctx.obj`` by the root callback; lazy so ``--help`` needs no credentials."""

    output_format: OutputFormat
    _credentials: Credentials | None = None
    _config: AppConfig | None = None
    _console: Console | None = None
    _clients: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_typer_context(cls, ctx: typer.Context) -> "AppContext":
        return ctx.obj

    @property
    def console(self) -> Console:
        if self._console is None:
            self._console = Console()
        return self._console

    @property
    def strategy(self) -> SerializationStrategy:
        return SerializationStrategy.from_format(self.output_format)

    def _client(self, name, factory):
        if name not in self._clients:
            self._credentials = self._credentials or Credentials()  # raises if env unset
            self._config = self._config or AppConfig()
            self._clients[name] = factory(
                oauth_token=self._credentials.oauth_token,
                organization_id=self._credentials.organization_id,
                timeout_seconds=int(self._config.timeout_seconds),
                retries=self._config.retries,
            )
        return self._clients[name]

    @property
    def tracker(self) -> TrackerClient:
        return self._client("tracker", TrackerClient)  # type: ignore[return-value]

    @property
    def wiki(self) -> WikiClient:
        return self._client("wiki", WikiClient)  # type: ignore[return-value]

    @property
    def forms(self) -> FormsClient:
        return self._client("forms", FormsClient)  # type: ignore[return-value]
```

- [ ] **Step 5: Wire the root callback** — in `cli.py`, give `_main` a `ctx: typer.Context` first parameter and store the `AppContext`:

```python
@app.callback()
def _main(
    ctx: typer.Context,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", "-o", help="Output format (auto = pretty on a TTY, JSON when piped)."),
    ] = OutputFormat.auto,
) -> None:
    """Declare the global ``--format`` option, configure logging, build the AppContext."""
    configure(level=AppConfig().log_level)
    ctx.obj = AppContext(output_format=output_format)
```

Add `from ycli.context import AppContext` to `cli.py`.

- [ ] **Step 6: Create the `_args.py` helpers.** `tracker/_args.py` holds the `KeyArg` alias (currently duplicated across 4 tracker `cli.py`) and the `parse_fields` function (moved verbatim from `tracker/_clideps.py`):

```python
"""Shared tracker CLI arg types + the ``--field key=value`` JSON-coerce helper."""
from __future__ import annotations

import json
from typing import Annotated, Any

import typer

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key, e.g. DATAENGINEERING-1.")]


def parse_fields(items: list[str] | None) -> dict[str, Any]:
    # ... body verbatim from tracker/_clideps.py:parse_fields ...
```

`forms/_args.py`:

```python
"""Shared forms CLI arg types."""
from __future__ import annotations

from typing import Annotated

import typer

SurveyIdArg = Annotated[
    str, typer.Argument(metavar="SURVEY_ID", help="Form id, e.g. 6818ceffe010db4f59d11329.")
]
```

- [ ] **Step 7: Sweep every CLI `cli.py`.** Apply this transform to each `cli.py` under `tracker/`, `wiki/`, `forms/` (NOT the `mcp.py` files):
  - Remove `from ycli.cliformat import output_format` and `from ycli.output import render`.
  - Remove `from ...._clideps import <domain>_client` (and `parse_fields`); import instead `from ycli.context import AppContext` and `from ycli.output import Serializer`. Tracker `cli.py` files that used `parse_fields`/`KeyArg` import them from `ycli.yandex.tracker._args`; forms from `ycli.yandex.forms._args`.
  - Replace every `render(<domain>_client(ctx).X.Y(...), output_format=output_format(ctx))` with:
    ```python
    app = AppContext.from_typer_context(ctx)
    Serializer.serialize(app.<domain>.X.Y(...), app.strategy, app.console)
    ```
  - Replace bare `<domain>_client(ctx)` (e.g. `wiki pages get`, which `print()`s `.content`) with `AppContext.from_typer_context(ctx).<domain>`.

  Worked example — `tracker/issues/cli.py` `get`/`list`/`create`:
  ```python
  from ycli.context import AppContext
  from ycli.output import Serializer
  from ycli.yandex.tracker._args import KeyArg, parse_fields

  @app.command()
  def get(ctx: typer.Context, key: KeyArg) -> None:
      """Print a single issue (full model) for KEY."""
      app_ctx = AppContext.from_typer_context(ctx)
      Serializer.serialize(app_ctx.tracker.issues.get(key), app_ctx.strategy, app_ctx.console)
  ```
  (The `full`/`count` commands that `print(json.dumps(...))` / `print(count)` keep their raw passthrough — only `render(...)` call sites change.)

  Files to sweep (every `cli.py` that imports `render`): tracker — `issues`, `comments`, `worklog`, `changelog`, `links`, `issuetypes`, `linktypes`, `priorities`, `transitions`, `me`; wiki — `pages`, `comments`, `attachments`, `me`; forms — `surveys`, `questions`, `answers`, `me`. (Confirm by `rg -l 'from ycli.output import render' src`.)

- [ ] **Step 8: Rewrite `auth.py`** (raw creds + probe loop, own carve-out, Serializer output):

```python
"""`ycli auth status` — validate credentials against each service's identity endpoint."""
from __future__ import annotations

from typing import Callable

import typer
from pydantic import ValidationError

from ycli.context import AppContext
from ycli.models import APIModel
from ycli.output import Serializer
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.settings import Credentials
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)


class ServiceAuthStatus(APIModel):
    service: str
    valid: bool = False
    identity: str | None = None
    detail: str = ""


class AuthReport(APIModel):
    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = []


_PROBES: list[tuple[str, type, Callable[[object], str]]] = [
    ("tracker", TrackerClient, lambda me: me.login),
    ("wiki", WikiClient, lambda me: me.username),
    ("forms", FormsClient, lambda me: me.email),
]


def _probe(name: str, client_cls: type, identity_of, credentials: Credentials) -> ServiceAuthStatus:
    client = client_cls(
        oauth_token=credentials.oauth_token, organization_id=credentials.organization_id
    )
    try:
        me = client.me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service=name, valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service=name, valid=False, detail=str(exc))
    return ServiceAuthStatus(service=name, valid=True, identity=identity_of(me))


@app.command()
def status(ctx: typer.Context) -> None:
    """Report whether the env credentials are set and actually work, per service."""
    app_ctx = AppContext.from_typer_context(ctx)
    env_names = {"oauth_token": "YANDEX_ID_OAUTH_TOKEN", "organization_id": "YANDEX_ID_ORGANIZATION_ID"}
    try:
        credentials = Credentials()
    except ValidationError as exc:
        missing = ", ".join(env_names.get(str(e["loc"][0]), str(e["loc"][0])) for e in exc.errors())
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        Serializer.serialize(AuthReport(configured=False, services=[]), app_ctx.strategy, app_ctx.console)
        raise typer.Exit(1) from None

    services = [_probe(name, cls, ident, credentials) for name, cls, ident in _PROBES]
    report = AuthReport(configured=True, organization_id=credentials.organization_id, services=services)
    Serializer.serialize(report, app_ctx.strategy, app_ctx.console)
    if not all(s.valid for s in services):
        raise typer.Exit(1)
```

- [ ] **Step 9: Delete the dead modules + the shim.** Delete `src/ycli/cliformat.py`, `tracker/_clideps.py`, `wiki/_clideps.py`, `forms/_clideps.py`. Remove the `render(...)` shim function from `output.py` (the `Serializer`/`from_format`/strategies stay). Delete `tests/test_cliformat.py`, `tests/yandex/tracker/test_clideps.py`, `tests/yandex/forms/test_clideps.py` (their behavior is now covered by `AppContext` + `_args` tests). Move any still-valuable `parse_fields` test cases into a new `tests/yandex/tracker/test_args.py`.

- [ ] **Step 10: Update CLI tests.** Each `test_cli.py` that drove a command previously relied on the lazy `<domain>_client(ctx)` (which built from env or was monkeypatched). They now need credentials in the env so `AppContext` can build the client. The standard pattern: `monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")`, `monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")`, then `@responses.activate` stubs the HTTP. Negative "missing credential" tests must `monkeypatch.chdir(tmp_path)` so a stray repo-root `.env` is not read. Run each `test_cli.py` and fix invocation/stub setup accordingly.

- [ ] **Step 11: Run the full CLI surface**

Run: `uv run pytest tests/test_yandex_cli.py tests/yandex -q -k "cli or auth or args or context"`
then the whole suite: `uv run pytest -q`
Expected: PASS (MCP still green via the temporary `from_env` shims). Coverage 100%.

- [ ] **Step 12: Regenerate snapshots if the CLI tree changed.** This task changes no command names or options yet (only bodies), so snapshots should be unchanged. If `tests/test_snapshots.py` fails, inspect the diff: only an intentional change is acceptable. Regenerate with `uv run python -m tests.snapshots` (per `tests/snapshots/__main__.py`) and review.

- [ ] **Step 13: Commit**

```bash
git add -A
git commit -m "refactor(di): raw-arg composition clients + AppContext; rewrite CLI call sites via Serializer; drop cliformat/_clideps/from_env(CLI)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: MCP `lifespan` composition root + remove `from_env`/`FromEnvSession`

**Files:**
- Modify: `src/ycli/mcp.py`, `tracker/_deps.py`, `wiki/_deps.py`, `forms/_deps.py`, the three composition `client.py` (drop the temporary `from_env` shim), `src/ycli/yandex/base.py` (delete `FromEnvSession`)
- Test: every `test_mcp.py` (`tests/yandex/**/test_mcp.py`, `tests/test_yandex_mcp.py`, `tests/test_plugin_mcp.py`, `tests/test_mcp_metadata.py`)

**Interfaces:**
- Consumes: the verified spike pattern from Task 4; raw-arg clients (Task 5).
- Produces: `mcp.py` root `lifespan` yielding `{"tracker": TrackerClient(...), "wiki": ..., "forms": ...}`; `_deps.py` providers returning `get_context().lifespan_context[<domain>]`.

- [ ] **Step 1: Write the failing test** — rewrite `tests/yandex/tracker/issues/test_mcp.py`'s injection to the lifespan model. Replace `_stub()` + `monkeypatch.setattr(..., "from_env", ...)` with a wrapper server that carries a test lifespan (per the Task 4 verified pattern). Add a helper at the top of the file:

```python
from contextlib import asynccontextmanager
from fastmcp import FastMCP, Client
from ycli.yandex.tracker.client import TrackerClient


def _served(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")

    @asynccontextmanager
    async def life(server):
        yield {"tracker": TrackerClient(oauth_token="t", organization_id="o")}

    wrapper = FastMCP("test", lifespan=life)
    wrapper.mount(issues_mcp.mcp)
    return wrapper
```

and rewrite one test to use it:

```python
@responses.activate
async def test_issues_get_tool(monkeypatch):
    responses.add(responses.GET, f"{BASE}/issues/DE-1", json={"key": "DE-1", "summary": "S"}, status=200)
    async with Client(_served(monkeypatch)) as client:
        result = await client.call_tool("issues_get", {"key": "DE-1"})
    assert result.data.key == "DE-1"
```

(If the Task 4 spike showed the provider must take `ctx: Context`, also apply that provider signature here.)

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/tracker/issues/test_mcp.py::test_issues_get_tool -v`
Expected: FAIL — the provider still calls `TrackerClient.from_env()` and there is no `lifespan_context` lookup yet (`KeyError`/attribute error), or the tool can't find the client.

- [ ] **Step 3: Add the shared MCP annotation module** `src/ycli/yandex/_mcp.py`:

```python
"""Shared FastMCP annotations + tag factory — de-dupes the per-domain _deps.py copies."""
from __future__ import annotations

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}


def tags(domain: str) -> set[str]:
    return {domain}
```

- [ ] **Step 4: Rewrite the three `_deps.py`.** Example — `tracker/_deps.py`:

```python
"""FastMCP dependency provider for the tracker subserver — reads the lifespan-built client."""
from fastmcp.server.dependencies import get_context

from ycli.yandex._mcp import RO, tags
from ycli.yandex.tracker.client import TrackerClient

TAGS = tags("tracker")


def tracker_client() -> TrackerClient:
    """Provide the lifespan-built TrackerClient to tracker MCP tools."""
    return get_context().lifespan_context["tracker"]
```

(Use the Task 4-verified signature: if the provider needs `ctx: Context`, declare it.) Apply identically to `wiki/_deps.py` (`"wiki"`) and `forms/_deps.py` (`"forms"`). The `RO`/`TAGS` symbols keep their names so `mcp.py` tool modules need no import changes.

- [ ] **Step 5: Add the lifespan to `mcp.py`:**

```python
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from ycli.log import configure
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.mcp import mcp as wiki_mcp


@asynccontextmanager
async def _lifespan(server):
    """Build the three domain clients once at startup from the env (the MCP composition root)."""
    credentials, config = Credentials(), AppConfig()
    kwargs = dict(
        oauth_token=credentials.oauth_token,
        organization_id=credentials.organization_id,
        timeout_seconds=int(config.timeout_seconds),
        retries=config.retries,
    )
    yield {
        "tracker": TrackerClient(**kwargs),
        "wiki": WikiClient(**kwargs),
        "forms": FormsClient(**kwargs),
    }


mcp = FastMCP("yandex", instructions=(...unchanged...), lifespan=_lifespan)
mcp.mount(wiki_mcp, namespace="wiki")
mcp.mount(tracker_mcp, namespace="tracker")
mcp.mount(forms_mcp, namespace="forms")
# main() unchanged — still calls configure(level=AppConfig().log_level) then mcp.run()
```

- [ ] **Step 6: Remove the transition scaffolding.** Delete the temporary `from_env` classmethod from `tracker/client.py`, `wiki/client.py`, `forms/client.py`. Delete the `FromEnvSession` class from `base.py` (and its now-unused `Self`, `AppConfig`, `Credentials`, `Transport` imports); `BaseYandex` keeps only `__init__(*, session)` + `base_url`. Update `base.py`'s module docstring (drop the `from_env` example).

- [ ] **Step 7: Migrate the rest of the MCP tests.** Apply the `_served(monkeypatch)` wrapper pattern from Step 1 to every test in `tests/yandex/tracker/issues/test_mcp.py`, `tests/yandex/wiki/test_mcp.py`, `tests/yandex/forms/test_mcp.py`, `tests/yandex/forms/me/test_mcp.py`, `tests/yandex/forms/surveys/test_mcp.py`. The integration test that already sets env vars and skips the stub keeps working (it exercises the real lifespan path). `tests/test_yandex_mcp.py` (tool counts) and `tests/test_mcp_metadata.py` only list tools — they need no client, but if they instantiate the root server they now require env creds at lifespan entry; if a list-tools call triggers lifespan, add the two `monkeypatch.setenv` lines.

- [ ] **Step 8: Run the MCP surface, then the whole suite**

Run: `uv run pytest tests/yandex -q -k mcp` then `uv run pytest -q`
Expected: PASS, 100% coverage. `rg -n "from_env|FromEnvSession" src` returns nothing.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "refactor(mcp): lifespan composition root reads env once; providers read lifespan_context; delete FromEnvSession

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## PHASE 3 — Configuration

### Task 7: add `YCLI_MAX_ITEMS` to `AppConfig`

**Files:**
- Modify: `src/ycli/yandex/settings.py`
- Test: `tests/yandex/test_settings.py`

**Interfaces:**
- Produces: `AppConfig.max_items: int` (default 500, env `YCLI_MAX_ITEMS`).

- [ ] **Step 1: Write the failing test** — add to `tests/yandex/test_settings.py`:

```python
def test_max_items_default_and_env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # ignore any repo-root .env
    monkeypatch.delenv("YCLI_MAX_ITEMS", raising=False)
    from ycli.yandex.settings import AppConfig
    assert AppConfig().max_items == 500
    monkeypatch.setenv("YCLI_MAX_ITEMS", "42")
    assert AppConfig().max_items == 42
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/test_settings.py::test_max_items_default_and_env -v`
Expected: FAIL — `AttributeError: 'AppConfig' object has no attribute 'max_items'`.

- [ ] **Step 3: Implement** — add the field to `AppConfig` (after `log_level`):

```python
    max_items: int = Field(default=500, validation_alias="YCLI_MAX_ITEMS")
```

- [ ] **Step 4: Run the test**

Run: `uv run pytest tests/yandex/test_settings.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/ycli/yandex/settings.py tests/yandex/test_settings.py
git commit -m "feat(config): add YCLI_MAX_ITEMS pagination cap (default 500)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## PHASE 4 — Bounded auto-pagination

### Task 8: `PaginationStrategy` ABC + concrete strategies

**Files:**
- Create: `src/ycli/yandex/pagination.py`
- Test: `tests/yandex/test_pagination.py`

**Interfaces:**
- Produces:
  - `class PaginationStrategy(ABC)` with `collect(self, fetch_page, limit: int | None) -> list`.
  - `SinglePageStrategy(extract)` — one call to `fetch_page(cursor=None)`, returns `extract(page)[:limit]`.
  - `CursorStrategy(extract, next_of)` — follows an opaque cursor (`next_of(page)`), accumulating `extract(page)` until exhausted or `limit` reached.
  - `NextUrlStrategy(extract, next_url_of, fetch_url)` — follows `next.next_url` (HATEOAS) until null or `limit`.
- These are pure (no HTTP) — `fetch_page`/`fetch_url` are injected callables, so they unit-test without `responses`.

- [ ] **Step 1: Write the failing tests** — `tests/yandex/test_pagination.py`:

```python
from ycli.yandex.pagination import SinglePageStrategy, CursorStrategy, NextUrlStrategy


def test_single_page_truncates_to_limit():
    page = {"results": [1, 2, 3, 4]}
    out = SinglePageStrategy(extract=lambda p: p["results"]).collect(lambda cursor: page, limit=2)
    assert out == [1, 2]


def test_single_page_none_limit_returns_all():
    page = {"results": [1, 2, 3]}
    out = SinglePageStrategy(extract=lambda p: p["results"]).collect(lambda cursor: page, limit=None)
    assert out == [1, 2, 3]


def test_cursor_strategy_drains_until_no_cursor():
    pages = {
        None: {"results": [1, 2], "next_cursor": "c1"},
        "c1": {"results": [3, 4], "next_cursor": None},
    }
    out = CursorStrategy(
        extract=lambda p: p["results"], next_of=lambda p: p["next_cursor"]
    ).collect(lambda cursor: pages[cursor], limit=None)
    assert out == [1, 2, 3, 4]


def test_cursor_strategy_respects_limit():
    pages = {None: {"results": [1, 2, 3, 4], "next_cursor": "c1"}}
    out = CursorStrategy(
        extract=lambda p: p["results"], next_of=lambda p: p["next_cursor"]
    ).collect(lambda cursor: pages[cursor], limit=3)
    assert out == [1, 2, 3]  # stops without fetching c1


def test_next_url_strategy_drains_and_dedupes_self_loops():
    pages = {
        "start": {"answers": [1], "next": {"next_url": "p2"}},
        "p2": {"answers": [2], "next": {"next_url": "p2"}},  # self-loop guard
    }
    out = NextUrlStrategy(
        extract=lambda p: p["answers"],
        next_url_of=lambda p: (p["next"] or {}).get("next_url"),
        fetch_url=lambda url: pages[url],
    ).collect(lambda cursor: pages["start"], limit=None)
    assert out == [1, 2]
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/test_pagination.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ycli.yandex.pagination'`.

- [ ] **Step 3: Implement `src/ycli/yandex/pagination.py`:**

```python
"""Pagination strategies — drain an API's page mechanics into a bounded flat list.

Each strategy owns ONE cursor mechanic and accepts injected page-access callables, so the
public client method never exposes a cursor: it picks a strategy, says how to read a page,
and gets back a list capped at ``limit`` (``None`` = uncapped). Pure — no HTTP here.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class PaginationStrategy(ABC):
    @abstractmethod
    def collect(self, fetch_page: Callable[[Any], Any], limit: int | None) -> list:
        """Accumulate items by driving ``fetch_page`` until exhausted or ``limit`` reached."""


class SinglePageStrategy(PaginationStrategy):
    def __init__(self, *, extract: Callable[[Any], list]) -> None:
        self._extract = extract

    def collect(self, fetch_page, limit):
        items = list(self._extract(fetch_page(None)))
        return items if limit is None else items[:limit]


class CursorStrategy(PaginationStrategy):
    def __init__(self, *, extract: Callable[[Any], list], next_of: Callable[[Any], Any]) -> None:
        self._extract = extract
        self._next_of = next_of

    def collect(self, fetch_page, limit):
        items: list = []
        cursor: Any = None
        while True:
            page = fetch_page(cursor)
            items.extend(self._extract(page))
            if limit is not None and len(items) >= limit:
                return items[:limit]
            cursor = self._next_of(page)
            if not cursor:
                return items


class NextUrlStrategy(PaginationStrategy):
    """HATEOAS: the first page comes from ``fetch_page``; subsequent ones from ``fetch_url``."""

    def __init__(
        self,
        *,
        extract: Callable[[Any], list],
        next_url_of: Callable[[Any], Any],
        fetch_url: Callable[[str], Any],
    ) -> None:
        self._extract = extract
        self._next_url_of = next_url_of
        self._fetch_url = fetch_url

    def collect(self, fetch_page, limit):
        page = fetch_page(None)
        items: list = list(self._extract(page))
        seen: set[str] = set()
        url = self._next_url_of(page)
        while url and url not in seen:
            if limit is not None and len(items) >= limit:
                break
            seen.add(url)
            page = self._fetch_url(url)
            items.extend(self._extract(page))
            url = self._next_url_of(page)
        return items if limit is None else items[:limit]
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/yandex/test_pagination.py -v`
Expected: PASS (all five).

- [ ] **Step 5: Commit**

```bash
git add src/ycli/yandex/pagination.py tests/yandex/test_pagination.py
git commit -m "feat(pagination): PaginationStrategy ABC + SinglePage/Cursor/NextUrl strategies

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 9: `wiki pages descendants` → bounded `CursorStrategy`, flat `PageRefList`

**Files:**
- Modify: `src/ycli/yandex/wiki/pages/models.py`, `wiki/pages/client.py`, `wiki/pages/cli.py`, `wiki/pages/mcp.py`
- Test: `tests/yandex/wiki/pages/test_client.py`, `test_cli.py`, `tests/yandex/wiki/test_mcp.py`, `tests/test_snapshots.py`

**Interfaces:**
- Produces: `PageRefList(RootModel[list[PageRef]])`; `PagesClient.descendants(slug, *, limit=None, actuality=None) -> PageRefList` (auto-drains). `DescendantsResponse` stays as the internal per-page parse type.
- Consumes: `CursorStrategy` (Task 8), `AppConfig.max_items` (Task 7).

- [ ] **Step 1: Write the failing test** — add to `tests/yandex/wiki/pages/test_client.py`:

```python
@responses.activate
def test_descendants_auto_drains_cursor(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t"); monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, f"{BASE}/pages/descendants",
                  json={"results": [{"id": 1, "slug": "a"}], "next_cursor": "c1"}, status=200)
    responses.add(responses.GET, f"{BASE}/pages/descendants",
                  json={"results": [{"id": 2, "slug": "b"}], "next_cursor": None}, status=200)
    client = WikiClient(oauth_token="t", organization_id="o")
    out = client.pages.descendants(slug="root")
    assert [r.slug for r in out.root] == ["a", "b"]
```

(`BASE = "https://api.wiki.yandex.net/v1"`; `WikiClient` import as in the existing test.)

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/wiki/pages/test_client.py::test_descendants_auto_drains_cursor -v`
Expected: FAIL — `descendants(...)` returns a single `DescendantsResponse`, so `.root` doesn't exist / only one page fetched.

- [ ] **Step 3: Add the flat collection** to `wiki/pages/models.py`:

```python
from pydantic import RootModel  # if not already imported

class PageRefList(RootModel[list[PageRef]]):
    """A drained, flat list of descendant page refs (no cursor — pagination is internal)."""
```

- [ ] **Step 4: Convert the client method.** In `wiki/pages/client.py`, keep the uplink request method but make it private/per-page (rename to `_descendants_page`) and add a public `descendants` that drives `CursorStrategy`. Because uplink methods must stay declarative, keep the decorated method and wrap it:

```python
import uplink
from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.pages.models import DescendantsResponse, PageDetails, PageRef, PageRefList


class PagesClient(WikiResource):
    @uplink.returns.json()
    @uplink.get("pages/descendants")
    def _descendants_page(
        self,
        slug: uplink.Query,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        actuality: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> DescendantsResponse:  # ty: ignore[empty-body]
        """One raw page of ``{id, slug}`` refs + ``next_cursor`` (internal — callers use ``descendants``)."""

    def descendants(self, slug: str, *, limit: int | None = None, actuality: str | None = None) -> PageRefList:
        """All descendant refs under ``slug``, draining ``next_cursor`` internally, capped at ``limit``."""
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        refs = strategy.collect(
            lambda cursor: self._descendants_page(slug=slug, page_size=100, cursor=cursor, actuality=actuality),
            limit,
        )
        return PageRefList(refs)
```

- [ ] **Step 5: Update CLI** — `wiki/pages/cli.py` `descendants`: replace `--cursor` with `--limit`/`--all`:

```python
@app.command()
def descendants(
    ctx: typer.Context,
    slug: SlugArg,
    limit: Annotated[int, typer.Option(help="Max refs (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every descendant (no cap).")] = False,
) -> None:
    """Print descendant slugs under SLUG (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or AppConfig().max_items)
    Serializer.serialize(app_ctx.wiki.pages.descendants(slug=slug, limit=cap), app_ctx.strategy, app_ctx.console)
```

(Import `AppConfig` from `ycli.yandex.settings`; `AppContext`/`Serializer` per Phase 2.)

- [ ] **Step 6: Update MCP** — `wiki/pages/mcp.py` `descendants`: drop `cursor`, default `limit` to the cap, return `PageRefList`; state the cap in the docstring:

```python
@mcp.tool(name="pages_descendants", annotations={**RO, "title": "List Wiki page descendants"}, tags=TAGS)
def descendants(slug: str, limit: int = 0, client: WikiClient = Depends(wiki_client)) -> PageRefList:
    """All descendant refs under SLUG, auto-paginated. Capped at YCLI_MAX_ITEMS (default 500)
    unless ``limit`` is given; narrow by SLUG for large trees."""
    cap = limit or AppConfig().max_items
    return client.pages.descendants(slug=slug, limit=cap)
```

(Import `PageRefList`, `AppConfig`.) The tool **name** is unchanged (`pages_descendants`) → MCP snapshot/tool-count stays at 25.

- [ ] **Step 7: Update existing tests + snapshots.** `test_pages_descendants_tool` (wiki `test_mcp.py`) asserted `.results[0].slug` and `.next_cursor` — change to `.root[0].slug` and drop the `next_cursor` assertion (no cursor in the public type). The CLI snapshot changes (the `descendants` options now `--limit`/`--all`, not `--cursor`) — regenerate `tests/snapshots/` and review the diff.

Run: `uv run pytest tests/yandex/wiki -q` then `uv run pytest tests/test_snapshots.py -q`
Expected: PASS after snapshot regen.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat(wiki): auto-paginate pages descendants (CursorStrategy) → flat PageRefList; --limit/--all

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 10: `forms answers` → `NextUrlStrategy`, bounded

**Files:**
- Modify: `src/ycli/yandex/forms/answers/client.py`, `forms/answers/cli.py`, `forms/answers/mcp.py`
- Test: `tests/yandex/forms/answers/test_client.py`, `test_cli.py`, `tests/yandex/forms/test_mcp.py`, `tests/test_snapshots.py`

**Interfaces:**
- Produces: `AnswersClient.list_all(survey_id, *, limit=None) -> AnswersResponse` — same envelope (columns + answers), answers bounded by `limit`, drained via `NextUrlStrategy`.
- Consumes: `NextUrlStrategy` (Task 8).

- [ ] **Step 1: Write the failing test** — add to `tests/yandex/forms/answers/test_client.py` a two-page drain that asserts the cap:

```python
@responses.activate
def test_list_all_respects_limit(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t"); monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, f"{BASE}/surveys/s1/answers",
                  json={"columns": [{"slug": "c"}], "answers": [{"id": 1}, {"id": 2}],
                        "next": {"next_url": "surveys/s1/answers?id=2"}}, status=200)
    client = FormsClient(oauth_token="t", organization_id="o")
    out = client.answers.list_all("s1", limit=1)
    assert len(out.answers) == 1
    assert out.next is None
```

(`BASE = "https://forms.yandex.net/..."` — match the existing answers test's base URL.)

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/forms/answers/test_client.py::test_list_all_respects_limit -v`
Expected: FAIL — `list_all()` takes no `limit` argument.

- [ ] **Step 3: Reimplement `list_all`** using `NextUrlStrategy` (replace the bespoke loop, keep the `urljoin`-based `fetch_url`):

```python
from urllib.parse import urljoin
from ycli.yandex.pagination import NextUrlStrategy


class AnswersClient(FormsResource):
    # ... the declarative `list` method unchanged (the per-page parser) ...

    def list_all(self, survey_id: str, *, limit: int | None = None) -> AnswersResponse:
        """Drain responses across pages (HATEOAS ``next.next_url``), capped at ``limit``.

        ``columns`` come from the first page; the merged ``next`` is always ``None``.
        """
        first = self.list(survey_id)
        columns = first.columns

        def fetch_url(url: str):
            absolute = urljoin(self.base_url.rstrip("/") + "/", url)
            return AnswersResponse.model_validate(self._session.get(absolute).json())

        answers = NextUrlStrategy(
            extract=lambda page: page.answers,
            next_url_of=lambda page: page.next.get("next_url") if isinstance(page.next, dict) else None,
            fetch_url=fetch_url,
        ).collect(lambda cursor: first, limit)
        return AnswersResponse(columns=columns, answers=answers, next=None)
```

- [ ] **Step 4: Thread `--limit`/`--all` through CLI + cap through MCP.** `forms/answers/cli.py`:

```python
@app.command("list")
def list_(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    limit: Annotated[int, typer.Option(help="Max responses (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every response (no cap).")] = False,
) -> None:
    """List a form's responses (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or AppConfig().max_items)
    Serializer.serialize(app_ctx.forms.answers.list_all(survey_id, limit=cap), app_ctx.strategy, app_ctx.console)
```

`forms/answers/mcp.py`: pass `limit=AppConfig().max_items` to `list_all`, state the cap in the docstring. Import `SurveyIdArg` from `ycli.yandex.forms._args`.

- [ ] **Step 5: Update tests + snapshots.** Keep the existing full-drain answers tests (they pass `limit=None` implicitly via `--all` or default); regenerate the CLI snapshot for the new `answers list` options.

Run: `uv run pytest tests/yandex/forms -q` then `uv run pytest tests/test_snapshots.py -q`
Expected: PASS after snapshot regen.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(forms): answers list_all via NextUrlStrategy, bounded by --limit/--all

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 11: single-page envelope unwraps → flat `RootModel` collections

Converts `wiki/comments`, `wiki/attachments`, and `forms/surveys` from returning `{results}`/`{result}` envelopes to flat `RootModel` collections via `SinglePageStrategy`. The envelope models become internal per-page parse types.

**Files:**
- Modify (3 endpoints × {models, client, cli, mcp}): `wiki/comments/*`, `wiki/attachments/*`, `forms/surveys/*`
- Test: the matching `test_client.py`/`test_cli.py`/`test_mcp.py` + `tests/test_snapshots.py`

**Interfaces:**
- Produces: `CommentList(RootModel[list[Comment]])` (wiki), `AttachmentList(RootModel[list[Attachment]])`, `SurveyCollection(RootModel[list[Survey]])`. Public list methods return these; `CommentsResponse`/`AttachmentsResponse`/`SurveyList` stay as internal per-page parsers.
- Consumes: `SinglePageStrategy` (Task 8).

- [ ] **Step 1: Write the failing test** — for wiki comments, add to `tests/yandex/wiki/comments/test_client.py`:

```python
@responses.activate
def test_list_returns_flat_collection(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t"); monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, f"{BASE}/pages/42/comments",
                  json={"results": [{"content": "hi"}]}, status=200)
    client = WikiClient(oauth_token="t", organization_id="o")
    out = client.comments.list(42)
    assert [c.content for c in out.root] == ["hi"]
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/yandex/wiki/comments/test_client.py::test_list_returns_flat_collection -v`
Expected: FAIL — `list()` returns `CommentsResponse` (`.results`), not a `RootModel` (`.root`).

- [ ] **Step 3: Apply the unwrap recipe to each of the 3 endpoints.** Per endpoint:
  - **models.py:** add the flat `RootModel` collection class (e.g. `class CommentList(RootModel[list[Comment]])`). Keep the envelope (`CommentsResponse`) — it's now the internal page parser.
  - **client.py:** rename the declarative uplink method to `_list_page` (returns the envelope), add a public `list` that runs `SinglePageStrategy`:
    ```python
    from ycli.yandex.pagination import SinglePageStrategy

    def list(self, page_id, *, limit: int | None = None) -> CommentList:
        items = SinglePageStrategy(extract=lambda page: page.results).collect(
            lambda cursor: self._list_page(page_id, page_size=100), limit
        )
        return CommentList(items)
    ```
    For `forms/surveys` the extract is `lambda page: page.result` (the envelope field is `result`, not `results`), and there is no `page_id`/`page_size`.
  - **cli.py:** the call site already became `Serializer.serialize(app.<domain>.<resource>.list(...), ...)` in Phase 2 — it now renders the flat collection; no option changes (single-page endpoints get no `--limit`/`--all`, per deviation #5).
  - **mcp.py:** change the tool's return annotation from the envelope to the flat collection (e.g. `-> CommentList`); the tool body `return client.comments.list(page_id)` is unchanged. Tool name unchanged → MCP tool count stays 25.

- [ ] **Step 4: Update existing tests.** The wiki `test_mcp.py` assertions `result.data.results[0].content` → `result.data.root[0].content`; `attachments` `.results[0].name` → `.root[0].name`; forms surveys `test_cli.py`/`test_mcp.py` `.result[...]` → `.root[...]`. Regenerate snapshots (no CLI option change expected; MCP tool list unchanged).

Run: `uv run pytest tests/yandex/wiki tests/yandex/forms/surveys -q` then `uv run pytest tests/test_snapshots.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(wiki,forms): unwrap comments/attachments/surveys envelopes to flat RootModel collections

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## PHASE 5 — Cleanups

### Task 12: arg/annotation dedupe, naming, scaffold

**Files:**
- Modify: the 4 tracker `cli.py` that inline `KeyArg` (point them at `tracker/_args.py` — partly done in Task 5; finish any stragglers), the 3 forms `cli.py` that inline `SurveyIdArg` (point at `forms/_args.py`), `scripts/new_endpoint.py`, and any `@app.callback()` group anchors for naming consistency.
- Test: the affected `test_cli.py`; add a scaffold smoke test if `scripts/new_endpoint.py` has one.

**Interfaces:** none new — this is consolidation.

- [ ] **Step 1: Dedupe `KeyArg` / `SurveyIdArg`.** `rg -n "KeyArg = Annotated" src` and `rg -n "SurveyIdArg = Annotated" src`; in each hit that is not the canonical `_args.py`, delete the local definition and import from `ycli.yandex.tracker._args` / `ycli.yandex.forms._args`. The tracker one with drifted help text (the spec noted one copy differs) is resolved by using the single canonical definition.

- [ ] **Step 2: Standardize the group-anchor naming.** Where resources define an empty `@app.callback()` to force subcommand dispatch, use a consistent name + docstring (`_group`, docstring: "Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."). `rg -n "@app.callback" src/ycli/yandex` to find them.

- [ ] **Step 3: Fix the scaffold template** — `scripts/new_endpoint.py`: update the generated `cli.py` template to emit the post-refactor pattern (`app_ctx = AppContext.from_typer_context(ctx); Serializer.serialize(result, app_ctx.strategy, app_ctx.console)`) with the right imports; generated `models.py` inherits `APIModel`; for a list endpoint, generate a `SinglePageStrategy`-based public method + flat `RootModel`. Update its `RO`/`_deps.py` references to `ycli.yandex._mcp`.

- [ ] **Step 4: Run the suite + a scaffold dry-run**

Run: `uv run pytest -q` and, if `new_endpoint.py` supports it, `uv run python scripts/new_endpoint.py --help` (or its dry-run) to confirm it imports.
Expected: PASS; `rg -n "KeyArg = Annotated|SurveyIdArg = Annotated" src` shows exactly one definition each.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(cli): dedupe KeyArg/SurveyIdArg into _args.py; consistent group anchors; fix scaffold template

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## PHASE 6 — Architecture invariants

### Task 13: rewrite `ARCHITECTURE.md` + `tests/test_architecture.py`

**Files:**
- Modify: `ARCHITECTURE.md`, `tests/test_architecture.py`
- Test: `tests/test_architecture.py` itself is the test.

**Interfaces:** none — this re-encodes the invariants the rest of the branch established.

- [ ] **Step 1: Update `ARCHITECTURE.md`.** Keep ARCH-1, ARCH-2, ARCH-3, ARCH-5, ARCH-6. Replace ARCH-4 and add ARCH-7..10 (copy the exact wording from the spec's "Architecture invariant changes" section, including the ARCH-10 carve-out for the SDK constructor defaults). Update the Layout block: drop `_clideps.py` from the per-domain line; note `src/ycli/models.py` (APIModel), `src/ycli/context.py` (AppContext), `src/ycli/yandex/pagination.py`, `src/ycli/yandex/_mcp.py`, `_args.py`.

- [ ] **Step 2: Write the new/changed checks** in `tests/test_architecture.py`:

```python
def test_arch4_serialization_confined_to_output():
    """Rendering goes through Serializer; model_dump_json + yaml.safe_dump only in output.py."""
    offenders = []
    for p in SRC.rglob("*.py"):
        if p.name == "output.py":
            continue
        text = p.read_text(encoding="utf-8")
        if "model_dump_json" in text or "yaml.safe_dump" in text:
            offenders.append(str(p.relative_to(SRC)))
    assert not offenders, f"serialization must live only in output.py; found in {offenders}"


def test_arch7_clients_never_resolve_credentials():
    """No client reads the env or constructs settings — credentials arrive as constructor args."""
    offenders = []
    for client in YANDEX.rglob("client.py"):
        text = client.read_text(encoding="utf-8")
        for needle in ("os.environ", "from_env", "Credentials(", "AppConfig("):
            if needle in text:
                offenders.append(f"{client.relative_to(SRC)}: {needle}")
    base = (YANDEX / "base.py").read_text(encoding="utf-8")
    for needle in ("os.environ", "from_env", "Credentials(", "AppConfig("):
        if needle in base:
            offenders.append(f"yandex/base.py: {needle}")
    assert not offenders, offenders


def test_arch8_single_config_source():
    """os.environ access and BaseSettings subclass definitions live only in settings.py."""
    offenders = []
    settings = YANDEX / "settings.py"
    for p in SRC.rglob("*.py"):
        if p == settings:
            continue
        text = p.read_text(encoding="utf-8")
        if "os.environ" in text:
            offenders.append(f"{p.relative_to(SRC)}: os.environ")
        if re.search(r"class \w+\(BaseSettings\)", text):
            offenders.append(f"{p.relative_to(SRC)}: BaseSettings subclass")
    assert not offenders, offenders


def test_arch10_no_uplink_timeout_shadow():
    """A configurable value is never overridden by a hardcoded literal at a call site."""
    offenders = [
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if "@uplink.timeout" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, f"@uplink.timeout shadows YCLI_TIMEOUT_SECONDS: {offenders}"


def test_arch10_sdk_defaults_match_appconfig():
    """The SDK constructor defaults (carve-out) stay equal to AppConfig's defaults."""
    import inspect
    from ycli.yandex.settings import AppConfig
    from ycli.yandex.tracker.client import TrackerClient
    params = inspect.signature(TrackerClient).parameters
    cfg = AppConfig()
    assert params["timeout_seconds"].default == int(cfg.timeout_seconds)
    assert params["retries"].default == cfg.retries
```

Replace the old `test_arch4_model_dump_json_only_in_output` with `test_arch4_serialization_confined_to_output`. Keep the ARCH-3 and ARCH-5 tests as-is (ARCH-5's org-header check still allows it only in `transport.py`). Update the module docstring to reference ARCH-1/2/3/4/5/6/7/8/9/10. ARCH-9 (typed boundary errors) is already covered by `tests/yandex/test_errors.py` + the absence of `raise_for_status` outside transport — add a grep check if not present:

```python
def test_arch9_no_status_branching_outside_transport():
    offenders = [
        str(p.relative_to(SRC))
        for p in SRC.rglob("*.py")
        if p.name != "transport.py" and "raise_for_status" in p.read_text(encoding="utf-8")
    ]
    assert not offenders, offenders
```

- [ ] **Step 3: Run the architecture + full suite**

Run: `uv run pytest tests/test_architecture.py -v` then `uv run pytest -q`
Expected: PASS — all invariants green, 100% coverage. If ARCH-7/8 flags a real leak, fix the source (not the test).

- [ ] **Step 4: Commit**

```bash
git add ARCHITECTURE.md tests/test_architecture.py
git commit -m "docs(arch): ARCH-4 serialization confinement; add ARCH-7..10 (DI, single config, typed errors, no-shadow)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Final verification (before finishing the branch)

- [ ] `uv run pytest -q` — full suite green, coverage 100%.
- [ ] `uv run lint-imports` — import-linter contracts pass.
- [ ] `rg -n "from_env|FromEnvSession|cliformat|_clideps|_STRATEGIES" src` — returns nothing (all removed).
- [ ] `rg -n "render\(" src/ycli` — only inside `output.py`'s strategies (the module-level `render` shim is gone).
- [ ] `uv run ycli --help` and `uv run ycli auth status` (with creds) smoke-run.
- [ ] Then use **superpowers:finishing-a-development-branch**: PR → explicit approval → squash-merge as `feat:` → v0.7.0 → verify PyPI → post-release `uv lock` + `build:` commit.
