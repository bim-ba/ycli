"""Tracker FastMCP domain server — reads-only tools, namespaced <resource>_<action>."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker import mcp as tracker_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


async def test_all_read_tools_registered():
    async with Client(tracker_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {
        "applications_list",
        "attachments_list",
        "autoactions_get",
        "autoactions_logs_get",
        "autoactions_logs_list",
        "boards_get",
        "boards_list",
        "bulk_get",
        "bulk_issues_list",
        "changelog_list",
        "checklists_get",
        "columns_get",
        "columns_list",
        "comments_list",
        "components_list",
        "entities_attachments_get",
        "entities_attachments_list",
        "entities_comments_get",
        "entities_comments_list",
        "entities_events_list",
        "entities_get",
        "entities_links_list",
        "entities_permissions_get",
        "entities_search",
        "fields_get",
        "fields_list",
        "filters_get",
        "issues_count",
        "issues_get",
        "issues_list",
        "issues_search",
        "issuetypes_list",
        "links_list",
        "linktypes_list",
        "localfields_get",
        "localfields_list",
        "macros_get",
        "macros_list",
        "me_get",
        "priorities_list",
        "queues_fields_list",
        "queues_get",
        "queues_list",
        "queues_tags_list",
        "queues_versions_list",
        "remotelinks_list",
        "resolutions_list",
        "sprints_get",
        "sprints_list",
        "statuses_list",
        "transitions_list",
        "triggers_get",
        "triggers_webhooklog_list",
        "users_get",
        "users_list",
        "worklog_list",
        "worklog_search",
    }


@responses.activate
async def test_priorities_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/priorities", json=[{"key": "normal"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("priorities_list", {})
    assert result.data[0].key == "normal"


@responses.activate
async def test_issuetypes_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/issuetypes", json=[{"key": "task"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("issuetypes_list", {})
    assert result.data[0].key == "task"


@responses.activate
async def test_linktypes_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/linktypes", json=[{"id": "relates"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("linktypes_list", {})
    assert result.data[0].id == "relates"


@responses.activate
async def test_comments_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/issues/DE-1/comments", json=[{"text": "hi"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("comments_list", {"key": "DE-1"})
    assert result.data[0].text == "hi"


@responses.activate
async def test_links_list_tool(creds):
    responses.add(
        responses.GET, f"{BASE}/issues/DE-1/links", json=[{"object": {"key": "DE-2"}}], status=200
    )
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("links_list", {"key": "DE-1"})
    assert result.data[0].object.key == "DE-2"


@responses.activate
async def test_transitions_list_tool(creds):
    responses.add(
        responses.GET, f"{BASE}/issues/DE-1/transitions", json=[{"id": "close"}], status=200
    )
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("transitions_list", {"key": "DE-1"})
    assert result.data[0].id == "close"


@responses.activate
async def test_worklog_list_tool(creds):
    responses.add(
        responses.GET, f"{BASE}/issues/DE-1/worklog", json=[{"duration": "PT2H"}], status=200
    )
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("worklog_list", {"key": "DE-1"})
    assert result.data[0].duration == "PT2H"


@responses.activate
async def test_changelog_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/issues/DE-1/changelog", json=[{"id": "1"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("changelog_list", {"key": "DE-1"})
    assert result.data[0].id == "1"
