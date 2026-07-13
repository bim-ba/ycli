"""TDD for the tracker autoactions MCP subserver — fastmcp Client against the resource server."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.autoactions import mcp as autoactions_mcp


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


async def test_autoactions_tools_registered():
    async with Client(autoactions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "autoactions_get",
        "autoactions_logs_list",
        "autoactions_logs_get",
        "autoactions_create",
    }
    read_tools = {"autoactions_get", "autoactions_logs_list", "autoactions_logs_get"}
    assert all(tools[name].annotations.readOnlyHint is True for name in read_tools)


@responses.activate
async def test_autoactions_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/queues/DESIGN/autoactions",
        json={"id": 10, "name": "nightly"},
        status=201,
    )
    async with Client(autoactions_mcp.mcp) as client:
        result = await client.call_tool(
            "autoactions_create",
            {"queue_id": "DESIGN", "body": {"name": "nightly", "actions": [{"type": "Update"}]}},
        )
    assert result.data.id == 10 and result.data.name == "nightly"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/queues/DESIGN/autoactions"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "nightly",
        "actions": [{"type": "Update"}],
    }


async def test_autoaction_write_tools_annotations():
    async with Client(autoactions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    ann = tools["autoactions_create"].annotations
    assert ann.readOnlyHint is False
    assert ann.destructiveHint is False
    assert ann.idempotentHint is False
    assert ann.title
