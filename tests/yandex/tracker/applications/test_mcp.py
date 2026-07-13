"""TDD for the Tracker external-applications MCP subserver."""

import pytest
import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.applications import mcp as applications_mcp

pytestmark = pytest.mark.integration


@responses.activate
async def test_applications_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/applications",
        json=[{"id": "my-application", "name": "Application name"}],
        status=200,
    )
    async with Client(applications_mcp.mcp) as client:
        result = await client.call_tool("applications_list", {})
    assert [a.id for a in result.data] == ["my-application"]


async def test_application_tool_registered_read_only():
    async with Client(applications_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"applications_list"}
    assert tools["applications_list"].annotations.readOnlyHint is True
