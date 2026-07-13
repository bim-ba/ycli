"""TDD for the tracker columns MCP subserver (fastmcp Client vs the resource subserver)."""

import json

import responses
from fastmcp import Client

from ycli.yandex.tracker.columns import mcp as columns_mcp

BASE = "https://api.tracker.yandex.net/v3"


@responses.activate
async def test_columns_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/boards/73/columns",
        json=[{"id": 1, "name": "Open"}],
        status=200,
    )
    async with Client(columns_mcp.mcp) as client:
        result = await client.call_tool("columns_list", {"board_id": 73})
    assert [c.name for c in result.data] == ["Open"]


@responses.activate
async def test_columns_get_tool(creds):
    responses.add(
        responses.GET, f"{BASE}/boards/73/columns/1", json={"id": 1, "name": "Open"}, status=200
    )
    async with Client(columns_mcp.mcp) as client:
        result = await client.call_tool("columns_get", {"board_id": 73, "column_id": 1})
    assert result.data.id == 1 and result.data.name == "Open"


async def test_column_tools_registered_read_only():
    async with Client(columns_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"columns_list", "columns_get"} <= set(tools)
    assert tools["columns_get"].annotations.readOnlyHint is True
    assert tools["columns_list"].annotations.readOnlyHint is True


@responses.activate
async def test_columns_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/boards/73/columns/", json={"id": 4, "name": "QA"}, status=201
    )
    async with Client(columns_mcp.mcp) as client:
        result = await client.call_tool(
            "columns_create", {"board_id": 73, "body": {"name": "QA", "statuses": ["open"]}}
        )
    assert result.data.name == "QA"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/boards/73/columns/"
    assert json.loads(responses.calls[0].request.body) == {"name": "QA", "statuses": ["open"]}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_columns_edit_tool(creds):
    responses.add(
        responses.PATCH, f"{BASE}/boards/73/columns/4", json={"id": 4, "name": "Review"}, status=200
    )
    async with Client(columns_mcp.mcp) as client:
        result = await client.call_tool(
            "columns_edit", {"board_id": 73, "column_id": 4, "body": {"name": "Review"}}
        )
    assert result.data.name == "Review"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"name": "Review"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_columns_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/boards/73/columns/4", status=204)
    async with Client(columns_mcp.mcp) as client:
        result = await client.call_tool("columns_delete", {"board_id": 73, "column_id": 4})
    assert result.data.ok is True and "4" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/boards/73/columns/4"


async def test_column_write_tools_annotations():
    async with Client(columns_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "columns_create": (False, False),
        "columns_edit": (False, True),
        "columns_delete": (True, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
