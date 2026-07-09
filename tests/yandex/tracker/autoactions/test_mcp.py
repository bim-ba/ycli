"""TDD for the tracker autoactions MCP subserver — fastmcp Client against the resource server."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.autoactions import mcp as autoactions_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_autoactions_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9",
        json={"id": 9, "name": "auto"},
        status=200,
    )
    async with Client(autoactions_mcp.mcp) as client:
        result = await client.call_tool("autoactions_get", {"queue_id": "DESIGN", "action_id": 9})
    assert result.data.id == 9 and result.data.name == "auto"


@responses.activate
async def test_autoactions_logs_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9/logs",
        json=[{"id": "x", "searchHits": 3}],
        status=200,
    )
    async with Client(autoactions_mcp.mcp) as client:
        result = await client.call_tool(
            "autoactions_logs_list", {"queue_id": "DESIGN", "action_id": 9}
        )
    assert result.data[0].id == "x"


@responses.activate
async def test_autoactions_logs_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/autoactions/9/logs/abc",
        json=[{"id": 0, "status": {"value": "success"}}],
        status=200,
    )
    async with Client(autoactions_mcp.mcp) as client:
        result = await client.call_tool(
            "autoactions_logs_get", {"queue_id": "DESIGN", "action_id": 9, "run_id": "abc"}
        )
    assert result.data[0].status.value == "success"


async def test_autoactions_tools_registered_read_only():
    async with Client(autoactions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"autoactions_get", "autoactions_logs_list", "autoactions_logs_get"}
    assert all(t.annotations.readOnlyHint is True for t in tools.values())
