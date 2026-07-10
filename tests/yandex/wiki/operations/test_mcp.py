"""TDD for the wiki /operations MCP subserver (read-only clone-status pollers)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.wiki.operations import mcp as operations_mcp

BASE = "https://api.wiki.yandex.net/v1"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_operations_clone_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone/task-1",
        json={"status": "success", "result": {"page": {"id": 42, "slug": "data/y"}}},
        status=200,
    )
    async with Client(operations_mcp.mcp) as client:
        result = await client.call_tool("operations_clone_get", {"task_id": "task-1"})
    assert result.data.status == "success"


@responses.activate
async def test_operations_gridclone_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone_inline_grid/task-1",
        json={"status": "success", "result": {"grid_id": "g2"}},
        status=200,
    )
    async with Client(operations_mcp.mcp) as client:
        result = await client.call_tool("operations_gridclone_get", {"task_id": "task-1"})
    assert result.data.result.grid_id == "g2"


async def test_operations_tools_are_read_only():
    async with Client(operations_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["operations_clone_get"].annotations.readOnlyHint is True
    assert tools["operations_gridclone_get"].annotations.readOnlyHint is True
