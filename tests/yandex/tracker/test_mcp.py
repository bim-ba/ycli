"""Tracker FastMCP domain server — read + write tools, namespaced <resource>_<action>."""

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker import mcp as tracker_mcp


async def test_all_tools_registered():
    async with Client(tracker_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {
        "applications_list",
        "attachments_list",
        "autoactions_create",
        "autoactions_get",
        "autoactions_logs_get",
        "autoactions_logs_list",
        "boards_create",
        "boards_delete",
        "boards_edit",
        "boards_get",
        "boards_list",
        "bulk_get",
        "bulk_issues_list",
        "bulk_move",
        "bulk_transition",
        "bulk_update",
        "changelog_list",
        "checklists_clear",
        "checklists_create",
        "checklists_delete",
        "checklists_edit",
        "checklists_get",
        "columns_create",
        "columns_delete",
        "columns_edit",
        "columns_get",
        "columns_list",
        "comments_add",
        "comments_delete",
        "comments_edit",
        "comments_list",
        "comments_react",
        "components_create",
        "components_edit",
        "components_list",
        "dashboards_add_cycle_time_widget",
        "dashboards_create",
        "entities_attachments_attach",
        "entities_attachments_delete",
        "entities_attachments_get",
        "entities_attachments_list",
        "entities_bulk_status_get",
        "entities_bulk_update",
        "entities_checklists_create",
        "entities_checklists_delete",
        "entities_checklists_delete_item",
        "entities_checklists_edit",
        "entities_checklists_edit_item",
        "entities_checklists_move",
        "entities_comments_create",
        "entities_comments_delete",
        "entities_comments_edit",
        "entities_comments_get",
        "entities_comments_list",
        "entities_comments_relative_list",
        "entities_create",
        "entities_create_report",
        "entities_delete",
        "entities_edit",
        "entities_events_list",
        "entities_get",
        "entities_links_create",
        "entities_links_delete",
        "entities_links_list",
        "entities_permissions_get",
        "entities_search",
        "entities_set_permissions",
        "fields_category_create",
        "fields_category_edit",
        "fields_create",
        "fields_edit",
        "fields_get",
        "fields_list",
        "filters_create",
        "filters_edit",
        "filters_get",
        "import_comment",
        "import_file",
        "import_link",
        "import_task",
        "import_worklog",
        "issues_count",
        "issues_create",
        "issues_get",
        "issues_list",
        "issues_move",
        "issues_scroll_clear",
        "issues_search",
        "issues_suggest",
        "issues_update",
        "issuetypes_create",
        "issuetypes_edit",
        "issuetypes_list",
        "links_add",
        "links_delete",
        "links_list",
        "linktypes_list",
        "localfields_create",
        "localfields_edit",
        "localfields_get",
        "localfields_list",
        "macros_create",
        "macros_delete",
        "macros_edit",
        "macros_get",
        "macros_list",
        "me_get",
        "priorities_create",
        "priorities_edit",
        "priorities_list",
        "queues_create",
        "queues_delete",
        "queues_fields_list",
        "queues_get",
        "queues_list",
        "queues_restore",
        "queues_set_permissions",
        "queues_tag_remove",
        "queues_tags_list",
        "queues_version_create",
        "queues_versions_list",
        "remotelinks_create",
        "remotelinks_delete",
        "remotelinks_list",
        "resolutions_create",
        "resolutions_edit",
        "resolutions_list",
        "sprints_archive",
        "sprints_create",
        "sprints_delete",
        "sprints_edit",
        "sprints_get",
        "sprints_list",
        "sprints_start",
        "statuses_create",
        "statuses_edit",
        "statuses_list",
        "transitions_execute",
        "transitions_list",
        "triggers_create",
        "triggers_edit",
        "triggers_get",
        "triggers_webhooklog_list",
        "users_get",
        "users_list",
        "worklog_create",
        "worklog_delete",
        "worklog_edit",
        "worklog_global_list",
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
    # Terminating page — without it the drain loop replays the first stub up to the cap.
    responses.add(responses.GET, f"{BASE}/issues/DE-1/changelog", json=[], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("changelog_list", {"key": "DE-1"})
    assert result.data[0].id == "1"
