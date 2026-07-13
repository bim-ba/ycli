"""TDD for the tracker sprints MCP subserver (fastmcp Client vs the resource subserver)."""

import json

import responses
from fastmcp import Client

from ycli.yandex.tracker.sprints import mcp as sprints_mcp

BASE = "https://api.tracker.yandex.net/v3"


@responses.activate
async def test_sprints_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/boards/3/sprints",
        json=[{"id": 4405, "name": "Sprint 1", "status": "in_progress"}],
        status=200,
    )
    async with Client(sprints_mcp.mcp) as client:
        result = await client.call_tool("sprints_list", {"board_id": 3})
    assert [s.name for s in result.data] == ["Sprint 1"]


@responses.activate
async def test_sprints_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/sprints/4405",
        json={"id": 4405, "name": "Sprint 1", "board": {"id": "3", "display": "My board"}},
        status=200,
    )
    async with Client(sprints_mcp.mcp) as client:
        result = await client.call_tool("sprints_get", {"sprint_id": 4405})
    assert result.data.id == 4405 and result.data.board.display == "My board"


async def test_sprint_tools_registered_read_only():
    async with Client(sprints_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"sprints_list", "sprints_get"} <= set(tools)
    assert tools["sprints_get"].annotations.readOnlyHint is True
    assert tools["sprints_list"].annotations.readOnlyHint is True


@responses.activate
async def test_sprints_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/sprints", json={"id": 5, "name": "S2"}, status=201)
    async with Client(sprints_mcp.mcp) as client:
        result = await client.call_tool(
            "sprints_create",
            {
                "body": {
                    "name": "S2",
                    "board": {"id": "3"},
                    "start_date": "2026-01-01",
                    "end_date": "2026-01-14",
                }
            },
        )
    assert result.data.name == "S2"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/sprints"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "S2",
        "board": {"id": "3"},
        "startDate": "2026-01-01",
        "endDate": "2026-01-14",
    }


@responses.activate
async def test_sprints_edit_tool_sends_version(creds):
    responses.add(responses.PATCH, f"{BASE}/sprints/5", json={"id": 5, "name": "S2x"}, status=200)
    async with Client(sprints_mcp.mcp) as client:
        result = await client.call_tool(
            "sprints_edit", {"sprint_id": 5, "body": {"name": "S2x"}, "version": 1}
        )
    assert result.data.name == "S2x"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"name": "S2x"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_sprints_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/sprints/5", status=204)
    async with Client(sprints_mcp.mcp) as client:
        result = await client.call_tool("sprints_delete", {"sprint_id": 5})
    assert result.data.ok is True and "5" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/sprints/5"


@responses.activate
async def test_sprints_start_tool_sends_version(creds):
    responses.add(
        responses.POST,
        f"{BASE}/sprints/5/_start",
        json={"id": 5, "status": "in_progress"},
        status=200,
    )
    async with Client(sprints_mcp.mcp) as client:
        result = await client.call_tool("sprints_start", {"sprint_id": 5, "version": 1})
    assert result.data.status == "in_progress"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/sprints/5/_start?version=1"


@responses.activate
async def test_sprints_archive_tool_sends_version(creds):
    responses.add(
        responses.POST, f"{BASE}/sprints/5/_archive", json={"id": 5, "archived": True}, status=200
    )
    async with Client(sprints_mcp.mcp) as client:
        result = await client.call_tool("sprints_archive", {"sprint_id": 5, "version": 2})
    assert result.data.id == 5
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/sprints/5/_archive?version=2"


async def test_sprint_write_tools_annotations():
    async with Client(sprints_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "sprints_create": (False, False),
        "sprints_edit": (False, True),
        "sprints_delete": (True, False),
        "sprints_start": (False, False),
        "sprints_archive": (False, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
