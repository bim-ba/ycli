# Endpoint authoring playbook (copy these patterns verbatim)

Companion to `2026-07-09-full-api-coverage-design.md`. Real test/code patterns extracted from the
existing suite. Every implementation agent reads THIS file first.

## Reference resources to copy from
- simple read: `src/ycli/yandex/tracker/priorities/` + `tests/yandex/tracker/priorities/`
- writes (POST+PATCH, body assertions): `src/ycli/yandex/tracker/issues/` + `tests/yandex/tracker/issues/`
- pagination draining: `src/ycli/yandex/wiki/pages/` (`descendants`) + `src/ycli/yandex/forms/answers/`
- MCP metadata + `meta` verb: `src/ycli/yandex/wiki/pages/mcp.py`
- new shared strategies/poller/binary: `src/ycli/yandex/pagination.py`, `.../polling.py`, `src/ycli/cli/binary.py`

## The 5 files (per resource) — see the spec's "Authoring standard". Key reminders:
- `client.py`: NO `from __future__ import annotations`. Subclass the domain base
  (`TrackerResource`/`WikiResource`/`FormsResource`) → carries `base_url`. Read =
  `@uplink.returns.json()` + `@uplink.get("path/{arg}")`, `arg: uplink.Path`, query = `uplink.Query`.
  Write = add `@uplink.json` + `body: uplink.Body`, verb `post/patch/delete`. Bare integer return
  (e.g. count) is fine. Binary = NO `@uplink.returns.json()`; return `requests.Response`, expose a
  public wrapper returning `resp.content` (bytes).
- `models.py`: `from __future__ import annotations`; inherit `APIModel`. Flat `XList(RootModel[list[X]])`
  public; envelope `XResponse(APIModel)` internal. EVERY field `Field(description="…")`. Typed write
  IN-models `XCreate`/`XUpdate`; discriminated unions (`Field(discriminator=…)`) where polymorphic.
- `cli.py`: `from __future__`; `typer.Typer(name=…, no_args_is_help=True)` + `@app.callback() def _group()`.
  Output via `Serializer.serialize(result, app_ctx.strategy, app_ctx.console)`. Scalar → `print(...)`.
  Binary → `from ycli.cli.binary import write_output`. `app_ctx = AppContext.from_typer_context(ctx)`.
- `mcp.py` (reads only): `from ycli.yandex.<domain>.dependencies import RO, TAGS, <domain>_client`.
  `@mcp.tool(name="<resource>_<verb>", annotations={**RO,"title":"…"}, tags=TAGS)`; docstring =
  description (2–4 sentences, max-metadata + a `>>>` example); return annotation = outputSchema;
  params `Annotated[type, Field(description="…")]`; `client: <Domain>Client = Depends(<domain>_client)`.
  verb ∈ {get,list,count,search,descendants,meta}. For a capped list add
  `cfg: AppConfig = Depends(app_config)` and `limit or cfg.max_items` (copy `wiki/pages/mcp.py::descendants`).

## Tests (tests/yandex/<domain>/<resource>/, add __init__.py) — REAL patterns

### test_client.py — `responses` stub + session DI
```python
import json, requests, responses
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.priorities.models import PriorityList
BASE = "https://api.tracker.yandex.net/v3"   # wiki: https://api.wiki.yandex.net/v1 ; forms: https://api.forms.yandex.net/v1

def _session():
    s = requests.Session(); s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"}); return s

@responses.activate
def test_list():
    responses.add(responses.GET, f"{BASE}/priorities", json=[{"key":"critical"}], status=200)
    out = PrioritiesClient(session=_session()).list()
    assert out.root[0].key == "critical"

@responses.activate
def test_create_posts_body():                      # writes: assert the sent body
    responses.add(responses.POST, f"{BASE}/issues/", json={"key":"DE-10"}, status=201)
    _client().create(body={"queue":"DE","summary":"New"})
    assert json.loads(responses.calls[0].request.body) == {"queue":"DE","summary":"New"}
```
For a binary download: `responses.add(..., body=b"\x89PNG...", status=200)` and assert the client returns those bytes.
For multi-page draining: use `responses.add_callback` returning page 1 with a cursor then page 2 with none
(copy `tests/yandex/forms/answers/test_client.py`); assert all items concatenated + `len(responses.calls)==2`.

### test_cli.py — Typer CliRunner + autouse creds
```python
import json, pytest, responses
from typer.testing import CliRunner
import ycli.cli.app as cli
BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()

@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN","t"); monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID","o")

@responses.activate
def test_get():
    responses.add(responses.GET, f"{BASE}/queues/DE", json={"id":1,"key":"DE"}, status=200)
    res = runner.invoke(cli.app, ["--format","json","tracker","queues","get","DE"])
    assert res.exit_code == 0 and json.loads(res.stdout)["key"] == "DE"
```
(NOTE: CLI tests invoke `cli.app` = the ROOT app, so they need the resource MOUNTED. Producer agents:
write these tests but they only pass AFTER the orchestrator/integrator wires the resource — the
integrator runs them. You self-validate test_client.py + test_models.py only.)

### test_mcp.py — fastmcp Client, async (asyncio_mode="auto", NO @pytest.mark.asyncio)
```python
import pytest, responses
from fastmcp import Client
from ycli.yandex.tracker.queues import mcp as queues_mcp   # resource subserver — no wiring needed
BASE = "https://api.tracker.yandex.net/v3"

@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN","t"); monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID","o")

@responses.activate
async def test_queues_get_tool(creds):
    responses.add(responses.GET, f"{BASE}/queues/DE", json={"id":1,"key":"DE"}, status=200)
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_get", {"queue_id":"DE"})
    assert result.data.key == "DE"

async def test_tool_read_only():
    async with Client(queues_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["queues_get"].annotations.readOnlyHint is True
```
MCP tests target the RESOURCE subserver (`queues_mcp.mcp`) → they DO NOT need wiring → self-validate them.
Reset caches: `tests/conftest.py` autouse clears the cached clients (no change needed for a new resource
in an existing domain).

## Coverage: 100% gate — every line/branch of new code runs. Each CLI option branch, each MCP tool,
each client method, pagination limit/empty branches. Bare `...` uplink bodies + `if TYPE_CHECKING:` are
auto-excluded. A new resource should need ZERO `# pragma: no cover`.

## Self-validation for PRODUCER agents (no wiring, no snapshots):
```
uv run ruff format <your new/edited files> ; uv run ruff check <files>
uv run pytest tests/yandex/<domain>/<resource>/test_client.py tests/yandex/<domain>/<resource>/test_models.py --no-cov -q
uv run pytest tests/yandex/<domain>/<resource>/test_mcp.py --no-cov -q   # if the resource has reads (MCP subserver test)
```
Report to the orchestrator: files created, and the exact wiring lines (import + `self.<r>=...Client(session=transport)`
in domain client.py; `app.add_typer(<r>_app)` in domain cli.py; `mcp.mount(<r>_mcp)` in domain mcp.py).

## Integrator agent (one, after producers): wires every new resource, then:
```
uv run python -m tests.snapshots --update      # regen cli_tree.txt + mcp_tools.txt
uv run ruff format --check . ; uv run ruff check . ; uv run lint-imports ; uv run ty check
uv run pytest                                  # 100% cov + ARCH-1..11 + snapshots — MUST be green
```
Fix integration/coverage gaps; never return red.
