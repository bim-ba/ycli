"""TDD for the tracker resolutions MCP subserver — reads + writes with honest annotations."""

import json

import responses
from fastmcp import Client

from ycli.yandex.tracker.resolutions import mcp as resolutions_mcp

BASE = "https://api.tracker.yandex.net/v3"


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


@responses.activate
async def test_resolutions_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/resolutions/", json={"id": 3, "key": "wontfix2"}, status=201
    )
    async with Client(resolutions_mcp.mcp) as client:
        result = await client.call_tool(
            "resolutions_create",
            {"body": {"key": "wontfix2", "name": {"ru": "Дубликат", "en": "Duplicate"}}},
        )
    assert result.data.key == "wontfix2"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/resolutions/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "key": "wontfix2",
        "name": {"ru": "Дубликат", "en": "Duplicate"},
    }


@responses.activate
async def test_resolutions_edit_tool_sends_version(creds):
    responses.add(
        responses.PATCH, f"{BASE}/resolutions/3", json={"id": 3, "key": "wontfix2"}, status=200
    )
    async with Client(resolutions_mcp.mcp) as client:
        result = await client.call_tool(
            "resolutions_edit", {"resolution_id": "3", "body": {"order": 7}, "version": 2}
        )
    assert result.data.id == 3
    assert responses.calls[0].request.method == "PATCH"
    assert "version=2" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"order": 7}  # ty: ignore[invalid-argument-type]


async def test_resolution_write_tools_annotations():
    async with Client(resolutions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "resolutions_create": (False, False),
        "resolutions_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
