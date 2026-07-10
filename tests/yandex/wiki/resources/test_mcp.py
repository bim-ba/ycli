"""Wiki /pages/{id}/resources FastMCP subserver tests (targets the resource subserver)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.wiki.resources import mcp as resources_mcp

BASE = "https://api.wiki.yandex.net/v1"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_resources_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/resources",
        json={"results": [{"type": "attachment", "item": {"name": "d.png"}}], "next_cursor": None},
        status=200,
    )
    async with Client(resources_mcp.mcp) as client:
        result = await client.call_tool("resources_list", {"page_id": 42})
    assert result.data[0].type == "attachment"


async def test_resources_list_is_registered_and_read_only():
    async with Client(resources_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "resources_list" in tools
    assert tools["resources_list"].annotations.readOnlyHint is True
