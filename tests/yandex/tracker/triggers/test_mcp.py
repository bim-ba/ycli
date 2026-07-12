"""TDD for the tracker triggers MCP subserver — fastmcp Client against the resource server."""

import json

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


async def test_triggers_tools_registered():
    async with Client(triggers_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "triggers_get",
        "triggers_webhooklog_list",
        "triggers_create",
        "triggers_edit",
    }
    read_tools = {"triggers_get", "triggers_webhooklog_list"}
    assert all(tools[name].annotations.readOnlyHint is True for name in read_tools)


@responses.activate
async def test_triggers_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/queues/DESIGN/triggers",
        json={"id": 17, "name": "notify"},
        status=201,
    )
    async with Client(triggers_mcp.mcp) as client:
        result = await client.call_tool(
            "triggers_create",
            {"queue_id": "DESIGN", "body": {"name": "notify", "actions": [{"type": "Webhook"}]}},
        )
    assert result.data.id == 17
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/queues/DESIGN/triggers"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "notify",
        "actions": [{"type": "Webhook"}],
    }


@responses.activate
async def test_triggers_edit_tool_sends_version(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/queues/DESIGN/triggers/17",
        json={"id": 17, "name": "renamed"},
        status=200,
    )
    async with Client(triggers_mcp.mcp) as client:
        result = await client.call_tool(
            "triggers_edit",
            {"queue_id": "DESIGN", "trigger_id": 17, "body": {"name": "renamed"}, "version": 2},
        )
    assert result.data.name == "renamed"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=2" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"name": "renamed"}  # ty: ignore[invalid-argument-type]


async def test_trigger_write_tools_annotations():
    async with Client(triggers_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "triggers_create": (False, False),
        "triggers_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
