"""TDD for the tracker changelog MCP subserver (fastmcp Client vs the resource subserver)."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.changelog import mcp as changelog_mcp


def _changelog_page_callback(request):
    """Two-page drain: page 1 (no id) → id=ch2 empty page terminates."""
    if "id=" in request.url:
        return (200, {}, json.dumps([]))
    body = [
        {"id": "ch1", "type": "IssueUpdated", "fields": []},
        {"id": "ch2", "type": "IssueCommentAdded", "fields": []},
    ]
    return (200, {}, json.dumps(body))


@responses.activate
async def test_changelog_list_tool_drains_pages(creds):
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/changelog",
        callback=_changelog_page_callback,
        content_type="application/json",
    )
    async with Client(changelog_mcp.mcp) as client:
        result = await client.call_tool("changelog_list", {"key": "DE-1"})
    assert [e.id for e in result.data] == ["ch1", "ch2"]  # both pages, joined in order
    assert len(responses.calls) == 2  # page 1 + the id=ch2 empty page


@responses.activate
async def test_changelog_list_tool_caps_with_explicit_limit(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/changelog",
        json=[{"id": "ch1", "fields": []}, {"id": "ch2", "fields": []}],
        status=200,
    )
    async with Client(changelog_mcp.mcp) as client:
        result = await client.call_tool("changelog_list", {"key": "DE-1", "limit": 1})
    assert [e.id for e in result.data] == ["ch1"]  # limit forwarded through the tool
    assert len(responses.calls) == 1


async def test_changelog_list_tool_registered_read_only():
    async with Client(changelog_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"changelog_list"}
    assert tools["changelog_list"].annotations.readOnlyHint is True
    assert tools["changelog_list"].annotations.title
