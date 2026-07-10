"""TDD for the tracker bulk MCP subserver — read tools only (bulk_get, bulk_issues_list)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.bulk import mcp as bulk_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_bulk_get_tool_returns_status(creds):
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab",
        json={"id": "1ab", "status": "COMPLETE"},
        status=200,
    )
    async with Client(bulk_mcp.mcp) as client:
        result = await client.call_tool("bulk_get", {"bulk_id": "1ab"})
    assert result.data.status == "COMPLETE"


@responses.activate
async def test_bulk_issues_list_tool_returns_data(creds):
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab/issues",
        json=[{"issue": {"key": "TEST-1"}, "status": "FAILED"}],
        status=200,
    )
    async with Client(bulk_mcp.mcp) as client:
        result = await client.call_tool("bulk_issues_list", {"bulk_id": "1ab"})
    assert [r.issue for r in result.data] == ["TEST-1"]


async def test_only_read_tools_exposed():
    async with Client(bulk_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"bulk_get", "bulk_issues_list"}


async def test_tools_are_read_only():
    async with Client(bulk_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["bulk_get"].annotations.readOnlyHint is True
    assert tools["bulk_issues_list"].annotations.readOnlyHint is True
