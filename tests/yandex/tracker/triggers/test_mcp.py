"""TDD for the tracker triggers MCP subserver — fastmcp Client against the resource server."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.triggers import mcp as triggers_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_triggers_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/DESIGN/triggers/16",
        json={"id": 16, "name": "trigger"},
        status=200,
    )
    async with Client(triggers_mcp.mcp) as client:
        result = await client.call_tool("triggers_get", {"queue_id": "DESIGN", "trigger_id": 16})
    assert result.data.id == 16 and result.data.name == "trigger"


@responses.activate
async def test_triggers_webhooklog_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/DEV/triggers/6/webhooks/log",
        json=[{"id": "x", "duration": 235}],
        status=200,
    )
    async with Client(triggers_mcp.mcp) as client:
        result = await client.call_tool(
            "triggers_webhooklog_list", {"queue_id": "DEV", "trigger_id": 6, "limit": 100}
        )
    assert result.data[0].duration == 235
    assert responses.calls[0].request.params["limit"] == "100"  # ty: ignore[unresolved-attribute]


async def test_triggers_tools_registered_read_only():
    async with Client(triggers_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"triggers_get", "triggers_webhooklog_list"}
    assert all(t.annotations.readOnlyHint is True for t in tools.values())
