"""TDD for the tracker boards MCP subserver (fastmcp Client vs the resource subserver)."""

import json

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.boards import mcp as boards_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_boards_get_tool(creds):
    responses.add(responses.GET, f"{BASE}/boards/1", json={"id": 1, "name": "My board"}, status=200)
    async with Client(boards_mcp.mcp) as client:
        result = await client.call_tool("boards_get", {"board_id": 1})
    assert result.data.id == 1 and result.data.name == "My board"


@responses.activate
async def test_boards_list_tool_caps_with_explicit_limit(creds):
    responses.add(
        responses.GET,
        f"{BASE}/boards/_paginate",
        json=[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
        status=200,
    )
    async with Client(boards_mcp.mcp) as client:
        result = await client.call_tool("boards_list", {"limit": 1})
    assert [b.name for b in result.data] == ["A"]  # limit forwarded through the tool
    assert len(responses.calls) == 1


@responses.activate
async def test_boards_list_tool_defaults_to_max_items(creds):
    # limit omitted (0) → cap falls back to cfg.max_items; empty page returns at once
    responses.add(responses.GET, f"{BASE}/boards/_paginate", json=[], status=200)
    async with Client(boards_mcp.mcp) as client:
        result = await client.call_tool("boards_list", {})
    assert list(result.data) == []


async def test_board_tools_registered_read_only():
    async with Client(boards_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"boards_get", "boards_list"} <= set(tools)
    assert tools["boards_get"].annotations.readOnlyHint is True
    assert tools["boards_list"].annotations.readOnlyHint is True


@responses.activate
async def test_boards_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/liveBoards/", json={"id": 9, "name": "Testing"}, status=201
    )
    async with Client(boards_mcp.mcp) as client:
        result = await client.call_tool(
            "boards_create", {"body": {"name": "Testing", "sprints_available": True}}
        )
    assert result.data.id == 9 and result.data.name == "Testing"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/liveBoards/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Testing",
        "sprintsAvailable": True,
    }


@responses.activate
async def test_boards_edit_tool(creds):
    responses.add(
        responses.PATCH, f"{BASE}/boards/9", json={"id": 9, "name": "New name"}, status=200
    )
    async with Client(boards_mcp.mcp) as client:
        result = await client.call_tool(
            "boards_edit", {"board_id": 9, "body": {"name": "New name"}}
        )
    assert result.data.name == "New name"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"name": "New name"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_boards_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/boards/9", status=204)
    async with Client(boards_mcp.mcp) as client:
        result = await client.call_tool("boards_delete", {"board_id": 9})
    assert result.data.ok is True and "9" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/boards/9"


async def test_board_write_tools_annotations():
    async with Client(boards_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "boards_create": (False, False),
        "boards_edit": (False, True),
        "boards_delete": (True, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
