"""TDD for the tracker statuses MCP subserver — reads + writes with honest annotations."""

import json

import responses
from fastmcp import Client

from ycli.yandex.tracker.statuses import mcp as statuses_mcp

BASE = "https://api.tracker.yandex.net/v3"


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


@responses.activate
async def test_statuses_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/statuses/", json={"id": 2, "key": "review"}, status=201)
    async with Client(statuses_mcp.mcp) as client:
        result = await client.call_tool(
            "statuses_create",
            {"body": {"key": "review", "name": {"ru": "Ревью", "en": "Review"}, "type": "paused"}},
        )
    assert result.data.key == "review"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/statuses/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "key": "review",
        "name": {"ru": "Ревью", "en": "Review"},
        "type": "paused",
    }


@responses.activate
async def test_statuses_edit_tool_sends_version(creds):
    responses.add(
        responses.PATCH, f"{BASE}/statuses/2", json={"id": 2, "key": "review"}, status=200
    )
    async with Client(statuses_mcp.mcp) as client:
        result = await client.call_tool(
            "statuses_edit", {"status_id": "2", "body": {"order": 5}, "version": 1}
        )
    assert result.data.id == 2
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"order": 5}  # ty: ignore[invalid-argument-type]


async def test_status_write_tools_annotations():
    async with Client(statuses_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "statuses_create": (False, False),
        "statuses_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
