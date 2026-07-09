"""TDD for the tracker macros MCP subserver — fastmcp Client against the resource server."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.macros import mcp as macros_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


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


async def test_macros_tools_registered_read_only():
    async with Client(macros_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"macros_list", "macros_get"}
    assert all(t.annotations.readOnlyHint is True for t in tools.values())
