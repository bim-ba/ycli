"""TDD for the tracker priorities MCP subserver — reads + writes with honest annotations."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.priorities import mcp as priorities_mcp


@responses.activate
async def test_priorities_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/priorities/", json={"id": 9, "key": "hotfix"}, status=201
    )
    async with Client(priorities_mcp.mcp) as client:
        result = await client.call_tool(
            "priorities_create",
            {"body": {"key": "hotfix", "name": {"ru": "Хотфикс", "en": "Hotfix"}}},
        )
    assert result.data.key == "hotfix"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/priorities/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "key": "hotfix",
        "name": {"ru": "Хотфикс", "en": "Hotfix"},
    }


@responses.activate
async def test_priorities_edit_tool_sends_version(creds):
    responses.add(
        responses.PATCH, f"{BASE}/priorities/9", json={"id": 9, "key": "hotfix"}, status=200
    )
    async with Client(priorities_mcp.mcp) as client:
        result = await client.call_tool(
            "priorities_edit",
            {"priority_id": "9", "body": {"description": "urgent"}, "version": 3},
        )
    assert result.data.key == "hotfix"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=3" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"description": "urgent"}  # ty: ignore[invalid-argument-type]


async def test_priority_tools_annotations():
    async with Client(priorities_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["priorities_list"].annotations.readOnlyHint is True
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "priorities_create": (False, False),
        "priorities_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
