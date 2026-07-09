"""TDD for the tracker queues MCP subserver — fastmcp Client against the resource server."""

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.tracker.queues import mcp as queues_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_queues_list_tool_returns_flat_collection(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"id": "3", "key": "TEST"}, {"id": "4", "key": "DEMO"}],
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_list", {})
    assert [q.key for q in result.data] == ["TEST", "DEMO"]


@responses.activate
async def test_queues_list_tool_honours_limit(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"key": "A"}, {"key": "B"}, {"key": "C"}],
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_list", {"limit": 1})
    assert [q.key for q in result.data] == ["A"]


@responses.activate
async def test_queues_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST",
        json={"id": "3", "key": "TEST", "name": "Test"},
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_get", {"queue_id": "TEST"})
    assert result.data.key == "TEST" and result.data.name == "Test"


@responses.activate
async def test_queues_get_empty_response_guard(creds):
    """200 with an empty body trips the not-found guard rather than returning a blank queue."""
    responses.add(responses.GET, f"{BASE}/queues/NOPE", json={}, status=200)
    async with Client(queues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("queues_get", {"queue_id": "NOPE"})


@responses.activate
async def test_queues_get_not_found_is_clean_error(creds):
    responses.add(responses.GET, f"{BASE}/queues/NOPE", json={"errors": {}}, status=404)
    async with Client(queues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("queues_get", {"queue_id": "NOPE"})


async def test_queues_tools_registered_read_only():
    async with Client(queues_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"queues_list", "queues_get"}
    assert tools["queues_list"].annotations.readOnlyHint is True
    assert tools["queues_get"].annotations.readOnlyHint is True
