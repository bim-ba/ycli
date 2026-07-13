"""TDD for the tracker attachments MCP subserver — LIST tool only, read-only, no downloads."""

import pytest
import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.attachments import mcp as attachments_mcp

pytestmark = pytest.mark.integration


@responses.activate
async def test_attachments_list_tool_returns_data(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/attachments",
        json=[{"id": "123", "name": "picture.jpg"}],
        status=200,
    )
    async with Client(attachments_mcp.mcp) as client:
        result = await client.call_tool("attachments_list", {"issue_key": "JUNE-2"})
    assert [a.name for a in result.data] == ["picture.jpg"]


async def test_only_list_tool_exposed_no_binary():
    """The subserver exposes ONLY attachments_list — no download/thumbnail tool."""
    async with Client(attachments_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"attachments_list"}


async def test_list_tool_is_read_only():
    async with Client(attachments_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["attachments_list"].annotations.readOnlyHint is True
