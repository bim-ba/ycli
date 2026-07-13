"""TDD for the tracker checklists MCP subserver — reads + writes with honest annotations."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.checklists import mcp as checklists_mcp


async def test_checklists_get_registered_read_only():
    async with Client(checklists_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "checklists_get" in tools
    assert tools["checklists_get"].annotations.readOnlyHint is True


@responses.activate
async def test_checklists_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/checklistItems",
        json=[{"id": "5f", "text": "step 1", "checked": False}],
        status=200,
    )
    async with Client(checklists_mcp.mcp) as client:
        result = await client.call_tool("checklists_get", {"key": "DE-1"})
    assert result.data[0].text == "step 1"


@responses.activate
async def test_checklists_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/checklistItems",
        json={"key": "DE-1", "checklistItems": [{"id": "5f", "text": "step 1"}]},
        status=201,
    )
    async with Client(checklists_mcp.mcp) as client:
        result = await client.call_tool(
            "checklists_create", {"key": "DE-1", "body": {"text": "step 1"}}
        )
    # Checklist.checklist_items round-trips through the output schema under its camelCase alias.
    assert result.structured_content["checklistItems"][0]["text"] == "step 1"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/checklistItems"
    assert json.loads(responses.calls[0].request.body) == {"text": "step 1"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_checklists_edit_tool(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/checklistItems/5f",
        json={"key": "DE-1", "checklistItems": [{"id": "5f", "text": "done", "checked": True}]},
        status=200,
    )
    async with Client(checklists_mcp.mcp) as client:
        result = await client.call_tool(
            "checklists_edit",
            {"key": "DE-1", "item_id": "5f", "body": {"text": "done", "checked": True}},
        )
    assert result.structured_content["checklistItems"][0]["checked"] is True
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"text": "done", "checked": True}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_checklists_delete_tool(creds):
    responses.add(
        responses.DELETE,
        f"{BASE}/issues/DE-1/checklistItems/5f",
        json={"key": "DE-1", "checklistItems": []},
        status=200,
    )
    async with Client(checklists_mcp.mcp) as client:
        result = await client.call_tool("checklists_delete", {"key": "DE-1", "item_id": "5f"})
    assert result.structured_content["checklistItems"] == []
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/checklistItems/5f"


@responses.activate
async def test_checklists_clear_tool(creds):
    responses.add(
        responses.DELETE,
        f"{BASE}/issues/DE-1/checklistItems",
        json={"key": "DE-1", "checklistItems": []},
        status=200,
    )
    async with Client(checklists_mcp.mcp) as client:
        result = await client.call_tool("checklists_clear", {"key": "DE-1"})
    assert result.data.key == "DE-1"
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/checklistItems"


async def test_checklist_write_tools_annotations():
    async with Client(checklists_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "checklists_create": (False, False),
        "checklists_edit": (False, True),
        "checklists_delete": (True, False),
        "checklists_clear": (True, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
