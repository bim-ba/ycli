"""TDD for the Tracker components MCP subserver."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.components import mcp as components_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_components_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/components", json=[{"id": 1, "name": "Test"}], status=200)
    async with Client(components_mcp.mcp) as client:
        result = await client.call_tool("components_list", {})
    assert [c.name for c in result.data] == ["Test"]


async def test_component_tool_registered_read_only():
    async with Client(components_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"components_list"}
    assert tools["components_list"].annotations.readOnlyHint is True
