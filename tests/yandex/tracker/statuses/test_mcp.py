"""TDD for the tracker statuses MCP subserver."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.statuses import mcp as statuses_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_statuses_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/statuses",
        json=[{"id": 1, "key": "open", "type": "new"}],
        status=200,
    )
    async with Client(statuses_mcp.mcp) as client:
        result = await client.call_tool("statuses_list", {})
    assert [s.key for s in result.data] == ["open"]


async def test_statuses_tool_read_only():
    async with Client(statuses_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "statuses_list" in tools
    assert tools["statuses_list"].annotations.readOnlyHint is True
