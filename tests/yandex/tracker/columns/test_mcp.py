"""TDD for the tracker columns MCP subserver (fastmcp Client vs the resource subserver)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.columns import mcp as columns_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


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
