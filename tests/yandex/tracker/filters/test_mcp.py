"""TDD for the Tracker filters MCP subserver — reads + writes with honest annotations."""

import json

import responses
from fastmcp import Client

from ycli.yandex.tracker.filters import mcp as filters_mcp

BASE = "https://api.tracker.yandex.net/v3"


@responses.activate
async def test_filters_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/filters/12345",
        json={"id": 12345, "name": "My open issues"},
        status=200,
    )
    async with Client(filters_mcp.mcp) as client:
        result = await client.call_tool("filters_get", {"filter_id": "12345"})
    assert result.data.id == 12345 and result.data.name == "My open issues"


async def test_filter_tool_registered_read_only():
    async with Client(filters_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"filters_get", "filters_create", "filters_edit"}
    assert tools["filters_get"].annotations.readOnlyHint is True


@responses.activate
async def test_filters_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/filters/", json={"id": 12346, "name": "Mine"}, status=201
    )
    async with Client(filters_mcp.mcp) as client:
        result = await client.call_tool(
            "filters_create", {"body": {"name": "Mine", "query": "Assignee: me()"}}
        )
    assert result.data.name == "Mine"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/filters/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Mine",
        "query": "Assignee: me()",
    }


@responses.activate
async def test_filters_edit_tool(creds):
    responses.add(
        responses.PATCH, f"{BASE}/filters/12346", json={"id": 12346, "name": "Renamed"}, status=200
    )
    async with Client(filters_mcp.mcp) as client:
        result = await client.call_tool(
            "filters_edit", {"filter_id": "12346", "body": {"name": "Renamed"}}
        )
    assert result.data.name == "Renamed"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"name": "Renamed"}  # ty: ignore[invalid-argument-type]


async def test_filter_write_tools_annotations():
    async with Client(filters_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "filters_create": (False, False),
        "filters_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
