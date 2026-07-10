"""TDD for the Tracker global-fields MCP subserver (fastmcp Client against the subserver)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.fields import mcp as fields_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_fields_list_tool(creds):
    responses.add(
        responses.GET, f"{BASE}/fields", json=[{"id": "summary"}, {"id": "status"}], status=200
    )
    async with Client(fields_mcp.mcp) as client:
        result = await client.call_tool("fields_list", {})
    assert [f.id for f in result.data] == ["summary", "status"]


@responses.activate
async def test_fields_get_tool(creds):
    responses.add(responses.GET, f"{BASE}/fields/ruName", json={"id": "ruName"}, status=200)
    async with Client(fields_mcp.mcp) as client:
        result = await client.call_tool("fields_get", {"field_id": "ruName"})
    assert result.data.id == "ruName"


async def test_field_tools_registered_read_only():
    async with Client(fields_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"fields_list", "fields_get"} <= set(tools)
    assert tools["fields_list"].annotations.readOnlyHint is True
    assert tools["fields_get"].annotations.readOnlyHint is True
