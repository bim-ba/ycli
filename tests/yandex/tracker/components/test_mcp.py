"""TDD for the Tracker components MCP subserver — reads + writes with honest annotations."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.components import mcp as components_mcp


@responses.activate
async def test_components_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/components", json=[{"id": 1, "name": "Test"}], status=200)
    async with Client(components_mcp.mcp) as client:
        result = await client.call_tool("components_list", {})
    assert [c.name for c in result.data] == ["Test"]


async def test_component_tool_registered_read_only():
    async with Client(components_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"components_list", "components_create", "components_edit"}
    assert tools["components_list"].annotations.readOnlyHint is True


@responses.activate
async def test_components_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/components", json={"id": 7, "name": "API"}, status=201)
    async with Client(components_mcp.mcp) as client:
        result = await client.call_tool(
            "components_create", {"body": {"name": "API", "queue": "DE"}}
        )
    assert result.data.name == "API"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/components"
    assert json.loads(responses.calls[0].request.body) == {"name": "API", "queue": "DE"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_components_edit_tool_sends_version(creds):
    responses.add(
        responses.PATCH, f"{BASE}/components/7", json={"id": 7, "name": "API v2"}, status=200
    )
    async with Client(components_mcp.mcp) as client:
        result = await client.call_tool(
            "components_edit", {"component_id": 7, "body": {"name": "API v2"}, "version": 4}
        )
    assert result.data.name == "API v2"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=4" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"name": "API v2"}  # ty: ignore[invalid-argument-type]


async def test_component_write_tools_annotations():
    async with Client(components_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "components_create": (False, False),
        "components_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
