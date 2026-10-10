"""`dry_run` on every tool that writes: one place takes the argument and answers the plan."""

import asyncio
import importlib
import inspect
import json
import pkgutil
from types import SimpleNamespace
from typing import Any, cast, get_type_hints

import mcp.types as mt
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import MiddlewareContext
from fastmcp.tools import Tool
from mcp.types import ToolAnnotations

import ycli.yandex
from tests.contract.test_contract import WRITE_CASES, _MCPSession, _serve
from tests.full_server import mcp
from ycli.yandex import mcp as layer
from ycli.yandex.mcp import DRY_RUN_SAID, PLAN_SCHEMA, RO, WRITE, DryRunOffered, new_server
from ycli.yandex.models import secret_keys
from ycli.yandex.registry import SERVICES
from ycli.yandex.tracker.client import TrackerClient

BOARD = "https://api.tracker.yandex.net/v3/boards/7"
UPDATE = ("tracker_boards_update", {"board_id": 7, "body": {"name": "New"}})


@pytest.fixture
def board(api):
    api.add("PATCH", BOARD, json={"id": 7})
    api.add("GET", BOARD, json={"id": 7})
    return api


async def _call(name: str, arguments: dict, server=mcp) -> dict:
    async with Client(server) as client:
        return (await client.call_tool(name, arguments)).structured_content or {}


async def test_a_plan_is_answered_and_nothing_is_sent(board):
    name, arguments = UPDATE
    planned = await _call(name, {**arguments, "dry_run": True})
    assert planned == {
        "dry_run": True,
        "request": {"method": "PATCH", "url": BOARD, "body": {"name": "New"}},
    }
    assert board.calls == []
    # `dry_run=false` is the call it always was.
    assert (await _call(name, {**arguments, "dry_run": False}))["id"] == 7
    assert [call.method for call in board.calls] == ["PATCH"]


async def test_a_tool_that_only_reads_has_no_such_argument(board):
    with pytest.raises(ToolError, match="dry_run: Unexpected keyword argument"):
        await _call("tracker_boards_get", {"board_id": 7, "dry_run": True})
    with pytest.raises(ToolError, match="dry_run: true or false"):
        await _call(UPDATE[0], {**UPDATE[1], "dry_run": "yes"})
    assert board.calls == []


async def test_calls_side_by_side_do_not_take_each_other_s_flag(board):
    """A real write is not stopped by a neighbour's flag; a plan never sends for want of its own."""
    name, arguments = UPDATE
    async with Client(mcp) as client:
        for _ in range(5):
            calls = [
                client.call_tool(name, {**arguments, "dry_run": index % 2 == 0})
                for index in range(8)
            ]
            answers = [answer.structured_content or {} for answer in await asyncio.gather(*calls)]
            assert [answer.get("dry_run", False) for answer in answers] == [True, False] * 4
    assert len(board.calls) == 5 * 4  # the four real ones of each round, and no plan
    assert layer._DRY_RUN.get() is None


async def test_the_flag_is_gone_after_a_call_that_failed(api):
    """A plan that could not be made (the read before the write failed) leaves nothing behind."""
    api.add("PATCH", BOARD, json={"id": 7})
    name, arguments = UPDATE
    with pytest.raises(ToolError, match="The arguments do not fit the tool"):
        await _call(name, {"board_id": "seven", "body": {}, "dry_run": True})
    assert layer._DRY_RUN.get() is None
    assert (await _call(name, arguments))["id"] == 7 and len(api.calls) == 1


def _own_server():
    """A server with two tools that are not ycli's: what the layer does to any tool."""
    server = new_server("own")

    @server.tool(annotations=WRITE)
    def unguarded() -> dict:
        """A tool that writes with a client it built by itself: the guard is not in it."""
        with TrackerClient(oauth_token="t", organization_id="o") as tracker:
            tracker.boards.delete(7)
        return {"deleted": 7}

    @server.tool(annotations=WRITE)
    def reads_only() -> dict:
        """Says it writes, and under `dry_run` only reads, through the guarded client."""
        with layer.client_provider(TrackerClient)() as tracker:
            return {"id": tracker.boards.get(7).id}

    return server


async def test_a_tool_whose_client_is_not_the_guarded_one_is_never_told_as_a_plan(api):
    """What the layer cannot stop it says: the architecture test below keeps it from happening."""
    api.add("DELETE", BOARD, status=204)
    with pytest.raises(ToolError, match="cannot be run with dry_run: it ran for real"):
        await _call("unguarded", {"dry_run": True}, _own_server())
    assert [call.method for call in api.calls] == ["DELETE"]


async def test_a_tool_that_would_write_nothing_says_so_and_gives_no_data(board):
    answered = await _call("reads_only", {"dry_run": True}, _own_server())
    assert answered == {"dry_run": True, "request": None}
    assert [call.method for call in board.calls] == ["GET"]


def _tool_functions():
    """Every tool function of every resource server of ycli, with the server's name."""
    for found in pkgutil.walk_packages(ycli.yandex.__path__, "ycli.yandex."):
        if found.name.rpartition(".")[2] != "mcp" or found.ispkg:
            continue
        server = getattr(importlib.import_module(found.name), "mcp", None)
        for tool in asyncio.run(server.list_tools()) if server is not None else []:
            yield found.name, tool


def test_every_tool_that_writes_takes_its_client_from_the_one_guarded_place():
    """ARCH-3: under `dry_run` no write can go, because no tool has another way to a service."""
    providers = {
        getattr(importlib.import_module(f"ycli.yandex.{service.name}.dependencies"), name)
        for service in SERVICES
        for name in [f"{service.name}_client"]
    }
    writing, wrong = 0, []
    for module, tool in _tool_functions():
        if not layer._writes(tool):
            continue
        writing += 1
        given = [
            getattr(parameter.default, "factory", None)
            for parameter in inspect.signature(tool.fn).parameters.values()
        ]
        # The one way in, and no second one beside it in the body of the tool.
        if not providers.intersection(given) or "build_client" in inspect.getsource(tool.fn):
            wrong.append(f"{module}:{tool.name}")
    assert not wrong
    assert writing == 260


async def test_a_secret_of_a_body_is_masked_in_the_plan_of_a_tool(api, monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")  # DataLens takes an IAM token only
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")
    body = {"name": "db", "type": "postgres", "password": "hunter2", "workbookId": "w1"}
    planned = await _call("datalens_connections_create", {"connection": body, "dry_run": True})
    assert "hunter2" not in str(planned) and api.calls == []
    assert planned["request"]["body"]["password"] == "***"


async def test_dry_run_is_listed_on_every_tool_that_writes_and_on_no_other():
    async with Client(mcp) as client:
        tools = await client.list_tools()
    offered = {tool.name for tool in tools if "dry_run" in tool.input_schema["properties"]}
    writing = {tool.name for tool in tools if tool.annotations.read_only_hint is False}
    assert offered == writing and len(offered) == 260
    said = {
        tool.input_schema["properties"]["dry_run"]["description"]
        for tool in tools
        if tool.name in offered
    }
    assert said == {DRY_RUN_SAID}


async def test_the_plan_stands_beside_the_tool_s_own_answer_in_its_output_schema():
    server = new_server("own")

    @server.tool(annotations=WRITE)
    def rename(name: str) -> dict[str, str]:
        """Rename it."""
        return {"name": name}

    @server.tool(annotations=RO)
    def read() -> dict[str, str]:
        """Read it."""
        return {}

    @server.tool(annotations=WRITE, output_schema=None)
    def touch() -> None:
        """Answers nothing, and has no schema to put a plan beside."""

    @server.tool(annotations=WRITE)
    def retag(tags: list[str]) -> list[str]:
        """Answers a list, which FastMCP puts under `result`."""
        with layer.client_provider(TrackerClient)() as tracker:
            tracker.boards.delete(7)
        return tags

    tools = {tool.name: tool for tool in await server.list_tools()}
    own = tools["read"].output_schema
    # The plan first: it takes no other key, so an answer of the tool is never read as one.
    assert tools["rename"].output_schema == {"type": "object", "anyOf": [PLAN_SCHEMA, own]}
    assert tools["touch"].output_schema is None
    assert "dry_run" in tools["touch"].parameters["properties"]
    wrapped = tools["retag"].output_schema
    assert wrapped is not None
    assert wrapped["x-fastmcp-wrap-result"] is True and wrapped["type"] == "object"
    assert wrapped["properties"]["result"]["anyOf"][0] == PLAN_SCHEMA
    # A client that validates what it gets takes both answers of both kinds of tool.
    async with Client(server) as client:
        assert (await client.call_tool("rename", {"name": "n"})).data == {"name": "n"}
        planned = await client.call_tool("retag", {"tags": ["a"], "dry_run": True})
        assert planned.structured_content == {
            "result": {"dry_run": True, "request": {"method": "DELETE", "url": BOARD, "body": None}}
        }
    assert "dry_run" not in tools["read"].parameters["properties"]
    # Passed through twice, as a server mounted in another is: nothing changes.
    [again] = await DryRunOffered().list_tools([tools["rename"]])
    assert again is tools["rename"]
    assert await DryRunOffered().get_tool("ghost", lambda name, *, version=None: _none()) is None


async def _none() -> None:
    return None


@pytest.mark.parametrize("ends", ["raises", "returns"])
async def test_the_flag_is_set_for_the_one_call_and_for_nothing_after_it(ends):
    """In the very context the call ran in: a server that served two calls in one would leak."""
    tool = Tool.from_function(
        lambda: {}, name="write", annotations=ToolAnnotations.model_validate(WRITE)
    )

    async def get_tool(name: str) -> Tool:
        return tool

    seen = []

    async def call_next(context):
        asked = layer._DRY_RUN.get()
        seen.append((asked is not None, context.message.arguments))
        if ends == "raises":
            raise ToolError("the service refused")
        assert asked is not None
        asked.guarded = True
        return None

    server = SimpleNamespace(fastmcp=SimpleNamespace(get_tool=get_tool))
    message = mt.CallToolRequestParams(name="write", arguments={"a": 1, "dry_run": True})
    context: Any = MiddlewareContext(message=message, fastmcp_context=cast("Any", server))
    if ends == "raises":
        with pytest.raises(ToolError, match="the service refused"):
            await layer.DryRun().on_call_tool(context, call_next)
    else:
        planned = await layer.DryRun().on_call_tool(context, call_next)
        assert planned.structured_content == {"dry_run": True, "request": None}
    assert seen == [(True, {"a": 1})]  # set for the call, and the argument taken out of it
    assert layer._DRY_RUN.get() is None


async def test_a_plan_that_would_grant_access_says_so(api):
    """A dry run of a grant tells the caller what the real call will be asked about."""
    body = {"role": "editor", "user": {"uid": "9001"}}
    planned = await _call("wiki_access_create", {"page_id": 7, "body": body, "dry_run": True})
    assert planned["grants_access"] is True and planned["request"]["method"] == "POST"
    assert "grants_access" not in await _call(UPDATE[0], {**UPDATE[1], "dry_run": True})
    assert api.calls == []


def _references(schema: Any) -> list[str]:
    """Every `$ref` of ``schema``, at any depth."""
    if isinstance(schema, dict):
        named = schema.get("$ref")
        own = [named] if isinstance(named, str) else []
        return own + [found for value in schema.values() for found in _references(value)]
    if isinstance(schema, list):
        return [found for value in schema for found in _references(value)]
    return []


def test_every_reference_of_the_output_schema_of_a_tool_that_writes_resolves():
    """The definitions a tool's schema refers to stay where its references look for them.

    The plan stands beside the tool's own schema; nested whole, that schema would keep its
    `$defs` under the union and its `$ref`s would point nowhere (#576).
    """
    looked, lost = 0, []
    for module, tool in _tool_functions():
        schema = tool.output_schema
        if not layer._writes(tool) or schema is None:
            continue
        looked += 1
        for reference in _references(schema):
            assert reference.startswith("#/$defs/"), reference
            if reference.removeprefix("#/$defs/") not in schema.get("$defs", {}):
                lost.append(f"{module}:{tool.name} {reference}")
    assert not lost[:5], f"{len(lost)} references point nowhere"
    assert looked > 200


SERVERS = {service.name: service.mcp_server() for service in SERVICES}
# The function of every tool, by the name the root server gives it: `<service>_<tool>`.
FUNCTIONS = {f"{module.split('.')[2]}_{tool.name}": tool.fn for module, tool in _tool_functions()}


def _listed(server) -> dict:
    return {tool.name: tool for tool in asyncio.run(server.list_tools())}


TOOLS = {name: _listed(server) for name, server in SERVERS.items()}


def _answers(case, wanted: str) -> bool:
    """Whether the tool of ``case`` has ``wanted`` at the root of its output schema."""
    assert case.mcp is not None
    tool = TOOLS[case.domain].get(case.mcp[0].removeprefix(f"{case.domain}_"))
    return tool is not None and wanted in (tool.output_schema or {})


def _function(name: str):
    """The function behind the tool ``name`` of the root server."""
    return FUNCTIONS[name]


PLANNED_AND_SENT = [
    case
    for service in SERVICES
    for wanted in ("$defs", "x-fastmcp-wrap-result")
    for case in [
        next(
            (
                case
                for case in WRITE_CASES
                if case.domain == service.name and _answers(case, wanted)
            ),
            None,
        )
    ]
    if case is not None
]


@pytest.mark.parametrize("case", PLANNED_AND_SENT, ids=[case.id for case in PLANNED_AND_SENT])
async def test_a_client_that_validates_takes_the_answer_and_the_plan(case, monkeypatch):
    """Both answers of a tool fit the schema a validating client holds them to.

    A service's server run by itself lists output schemas, and FastMCP's client checks every
    answer against them: a tool whose schema has definitions, and one that answers a list.
    """
    assert case.mcp is not None
    name, arguments = case.mcp
    local = name.removeprefix(f"{case.domain}_")
    for variable, value in case.env.items():
        monkeypatch.setenv(variable, value)
    api = _serve(monkeypatch, case)
    async with Client(SERVERS[case.domain]) as client:
        listed = {tool.name: tool for tool in await client.list_tools()}
        assert listed[local].output_schema is not None
        planned = await client.call_tool(local, {**arguments, "dry_run": True})
        plan = planned.structured_content or {}
        assert plan.get("result", plan)["dry_run"] is True
        assert all(sent.method == "GET" for sent in api.calls)
        answered = await client.call_tool(local, dict(arguments))
    assert not answered.is_error and len(api.calls) >= 1


async def test_a_part_of_the_reply_of_a_tool_that_writes_is_still_found_by_schema_get():
    async with Client(mcp) as client:
        found = await client.call_tool(
            "schema_get", {"tool": "tracker_boards_update", "name": "Calendar"}
        )
    assert not found.is_error and "properties" in str(found.structured_content)


NESTED = ("dry_run", "dryRun", "dry-run")


def _with_inside(arguments: dict, key: str) -> list[dict]:
    """``arguments`` with ``key: true`` put inside each object among them, at two depths."""
    made = []
    for name, value in arguments.items():
        if isinstance(value, dict):
            made.append({**arguments, name: {**value, key: True}})
            made.append({**arguments, name: {**value, "deeper": [{key: True}]}})
    return made


@pytest.mark.parametrize("case", WRITE_CASES, ids=[case.id for case in WRITE_CASES])
async def test_dry_run_inside_an_argument_is_refused_and_nothing_is_sent(case, monkeypatch):
    """One who nests it believes they are planning: that belief must not end in a write."""
    assert case.mcp is not None
    name, arguments = case.mcp
    for variable, value in case.env.items():
        monkeypatch.setenv(variable, value)
    api = _serve(monkeypatch, case)
    tried = [made for key in NESTED for made in _with_inside(dict(arguments), key)]
    async with Client(mcp) as client:
        for made in tried:
            refused = await client.call_tool(name, made, raise_on_error=False)
            assert refused.is_error, made
            assert "is the tool's own argument: give it beside" in refused.content[0].text
    assert api.calls == []


async def test_a_plan_is_no_error_in_the_log(board, caplog):
    """Two plans, and not a line that says a tool failed, nor a traceback of the signal."""
    caplog.set_level("DEBUG")
    name, arguments = UPDATE
    for _ in range(2):
        await _call(name, {**arguments, "dry_run": True})
    assert "Error calling tool" not in caplog.text and "RequestPlanned" not in caplog.text
    assert not [record for record in caplog.records if record.exc_info]


def test_no_secret_given_to_a_tool_comes_back_in_its_plan(monkeypatch):
    """Not by the function that masks: the literal value given is looked for in the answer.

    The parity of the two surfaces cannot see masking switched off, since both print the plan
    with one function. No contract case gives a secret, so one is put in: for every write case
    whose argument is a model that marks keys as secret, each such key is given a value of its
    own, the call is planned, and that value must not be in what comes back.
    """
    session, kept, unplaced = _MCPSession(), set(), set()
    try:
        for case in WRITE_CASES:
            assert case.mcp is not None
            name, arguments = case.mcp
            hints = get_type_hints(_function(name))
            for argument, value in arguments.items():
                model = hints.get(argument)
                if not isinstance(value, dict) or not isinstance(model, type):
                    continue
                for key in sorted(secret_keys(model)):
                    given = f"s3cr3t-of-{key}"
                    for variable, set_to in case.env.items():
                        monkeypatch.setenv(variable, set_to)
                    _serve(monkeypatch, case)
                    made = {**arguments, argument: {**value, key: given}, "dry_run": True}
                    try:
                        answered = json.dumps(session.call(name, made))
                    except ToolError:
                        unplaced.add((name, key))  # the key lies deeper in this model
                        continue
                    assert given not in answered, f"{name}: {key} came back in the plan"
                    assert "***" in answered, f"{name}: {key} is not in the plan at all"
                    kept.add((name, key))
    finally:
        session.close()
    assert len(kept) >= 10, sorted(unplaced)
