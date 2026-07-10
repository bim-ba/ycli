"""TDD for the tracker sprints MCP subserver (fastmcp Client vs the resource subserver)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.sprints import mcp as sprints_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


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
