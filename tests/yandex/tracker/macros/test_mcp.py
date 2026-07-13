"""TDD for the tracker macros MCP subserver — fastmcp Client against the resource server."""

import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.macros import mcp as macros_mcp

pytestmark = pytest.mark.integration


@responses.activate
async def test_macros_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/macros",
        json=[{"id": 3, "name": "a"}, {"id": 4, "name": "b"}],
        status=200,
    )
    async with Client(macros_mcp.mcp) as client:
        result = await client.call_tool("macros_list", {"queue_id": "TEST"})
    assert [m.name for m in result.data] == ["a", "b"]


@responses.activate
async def test_macros_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/macros/3",
        json={"id": 3, "name": "My macro"},
        status=200,
    )
    async with Client(macros_mcp.mcp) as client:
        result = await client.call_tool("macros_get", {"queue_id": "TEST", "macro_id": 3})
    assert result.data.id == 3 and result.data.name == "My macro"


async def test_macros_tools_registered():
    async with Client(macros_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "macros_list",
        "macros_get",
        "macros_create",
        "macros_edit",
        "macros_delete",
    }
    assert tools["macros_list"].annotations.readOnlyHint is True
    assert tools["macros_get"].annotations.readOnlyHint is True


@responses.activate
async def test_macros_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/queues/TEST/macros", json={"id": 5, "name": "Close it"}, status=201
    )
    async with Client(macros_mcp.mcp) as client:
        result = await client.call_tool(
            "macros_create", {"queue_id": "TEST", "body": {"name": "Close it", "body": "Done!"}}
        )
    assert result.data.name == "Close it"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/queues/TEST/macros"
    assert json.loads(responses.calls[0].request.body) == {"name": "Close it", "body": "Done!"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_macros_edit_tool(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/TEST/macros/5",
        json={"id": 5, "name": "Renamed"},
        status=200,
    )
    async with Client(macros_mcp.mcp) as client:
        result = await client.call_tool(
            "macros_edit", {"queue_id": "TEST", "macro_id": 5, "body": {"name": "Renamed"}}
        )
    assert result.data.name == "Renamed"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"name": "Renamed"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_macros_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/queues/TEST/macros/5", status=204)
    async with Client(macros_mcp.mcp) as client:
        result = await client.call_tool("macros_delete", {"queue_id": "TEST", "macro_id": 5})
    assert result.data.ok is True and "5" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/queues/TEST/macros/5"


async def test_macro_write_tools_annotations():
    async with Client(macros_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "macros_create": (False, False),
        "macros_edit": (False, True),
        "macros_delete": (True, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
