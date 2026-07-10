"""TDD for the Tracker filters MCP subserver."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.filters import mcp as filters_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


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
    assert set(tools) == {"filters_get"}
    assert tools["filters_get"].annotations.readOnlyHint is True
