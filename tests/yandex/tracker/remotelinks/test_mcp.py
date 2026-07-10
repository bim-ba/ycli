"""TDD for the tracker remotelinks MCP subserver — LIST tool only, read-only."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.remotelinks import mcp as remotelinks_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_remotelinks_list_tool_returns_data(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/remotelinks",
        json=[{"id": 51, "object": {"key": "TEST-17"}}],
        status=200,
    )
    async with Client(remotelinks_mcp.mcp) as client:
        result = await client.call_tool("remotelinks_list", {"issue_key": "JUNE-2"})
    assert [link.object.key for link in result.data] == ["TEST-17"]


async def test_only_list_tool_exposed():
    async with Client(remotelinks_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"remotelinks_list"}


async def test_list_tool_is_read_only():
    async with Client(remotelinks_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["remotelinks_list"].annotations.readOnlyHint is True
