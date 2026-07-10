"""TDD for the tracker resolutions MCP subserver."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.resolutions import mcp as resolutions_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_resolutions_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/resolutions",
        json=[{"id": 1, "key": "fixed", "name": "Решен"}],
        status=200,
    )
    async with Client(resolutions_mcp.mcp) as client:
        result = await client.call_tool("resolutions_list", {})
    assert [r.key for r in result.data] == ["fixed"]


async def test_resolutions_tool_read_only():
    async with Client(resolutions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "resolutions_list" in tools
    assert tools["resolutions_list"].annotations.readOnlyHint is True
