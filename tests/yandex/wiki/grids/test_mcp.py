"""TDD for the wiki /grids MCP subserver (read-only ``grids_get``)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.wiki.grids import mcp as grids_mcp

BASE = "https://api.wiki.yandex.net/v1"
GID = "g-uuid"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_grids_get_tool_returns_grid(creds):
    responses.add(
        responses.GET,
        f"{BASE}/grids/{GID}",
        json={"id": GID, "title": "Roadmap", "revision": "3"},
        status=200,
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool("grids_get", {"grid_id": GID})
    assert result.data.title == "Roadmap"
    assert result.data.revision == "3"


@responses.activate
async def test_grids_get_forwards_query_params(creds):
    responses.add(responses.GET, f"{BASE}/grids/{GID}", json={"id": GID}, status=200)
    async with Client(grids_mcp.mcp) as client:
        await client.call_tool("grids_get", {"grid_id": GID, "only_cols": "name"})
    assert responses.calls[0].request.params["only_cols"] == "name"  # ty: ignore[unresolved-attribute]


async def test_grids_get_is_read_only():
    async with Client(grids_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["grids_get"].annotations.readOnlyHint is True
