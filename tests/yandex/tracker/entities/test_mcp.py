"""TDD for the tracker entities MCP subserver — reads + writes with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.entities import mcp as entities_mcp

BASE = "https://api.tracker.yandex.net/v3"

READ_TOOLS = {
    "entities_get",
    "entities_search",
    "entities_events_list",
    "entities_permissions_get",
    "entities_comments_list",
    "entities_comments_get",
    "entities_comments_relative_list",
    "entities_links_list",
    "entities_attachments_list",
    "entities_attachments_get",
    "entities_bulk_status_get",
}

# tool -> (destructiveHint, idempotentHint)
WRITE_TOOLS = {
    "entities_create": (False, False),
    "entities_edit": (False, True),
    "entities_delete": (True, False),
    "entities_set_permissions": (False, True),
    "entities_bulk_update": (False, True),
    "entities_create_report": (False, False),
    "entities_comments_create": (False, False),
    "entities_comments_edit": (False, True),
    "entities_comments_delete": (True, False),
    "entities_checklists_create": (False, False),
    "entities_checklists_edit": (False, True),
    "entities_checklists_edit_item": (False, True),
    "entities_checklists_delete": (True, False),
    "entities_checklists_delete_item": (True, False),
    "entities_checklists_move": (False, False),
    "entities_links_create": (False, False),
    "entities_links_delete": (True, False),
    "entities_attachments_attach": (False, False),
    "entities_attachments_delete": (True, False),
}


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


async def test_exposes_exactly_the_expected_tools():
    async with Client(entities_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == READ_TOOLS | set(WRITE_TOOLS)


async def test_read_tools_are_read_only():
    async with Client(entities_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    for name in READ_TOOLS:
        assert tools[name].annotations.readOnlyHint is True, name


async def test_write_tools_annotations():
    async with Client(entities_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    for name, (destructive, idempotent) in WRITE_TOOLS.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name


@responses.activate
async def test_entities_get_tool_returns_entity(creds):
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f",
        json={"id": "655f", "entityType": "project", "fields": {"summary": "Q4"}},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_get", {"entity_type": "project", "entity_id": "655f", "fields": "summary"}
        )
    assert result.data.id == "655f" and result.data.fields.summary == "Q4"


@responses.activate
async def test_entities_search_tool_returns_list(creds):
    responses.add(
        responses.POST,
        f"{BASE}/entities/goal/_search",
        json={"values": [{"id": "1"}, {"id": "2"}]},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_search",
            {"entity_type": "goal", "input_text": "Q4", "order_by": "entityStatus"},
        )
    assert [e.id for e in result.data] == ["1", "2"]
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "input": "Q4",
        "orderBy": "entityStatus",
    }


def _events_callback(request):
    """First page → one event, second page (from=e1) empty, so the drain terminates."""
    from urllib.parse import parse_qs, urlparse

    if "from" in parse_qs(urlparse(request.url).query):
        return (200, {}, '{"events": [], "hasNext": false}')
    return (200, {}, '{"events": [{"id": "e1", "display": "Issue updated"}], "hasNext": true}')


@responses.activate
async def test_entities_events_list_tool(creds):
    responses.add_callback(
        responses.GET,
        f"{BASE}/entities/project/655f/events/_relative",
        callback=_events_callback,
        content_type="application/json",
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_events_list", {"entity_type": "project", "entity_id": "655f", "limit": 5}
        )
    assert [e.display for e in result.data] == ["Issue updated"]


@responses.activate
async def test_entities_permissions_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/extendedPermissions",
        json={"acl": {"READ": {"roles": ["OWNER"]}}},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_permissions_get", {"entity_type": "project", "entity_id": "655f"}
        )
    # ExtendedPermissions.acl uses uppercase serialization aliases (READ/WRITE/GRANT); assert on
    # the raw structured content, which round-trips those aliases faithfully.
    assert result.structured_content["acl"]["READ"]["roles"] == ["OWNER"]


@responses.activate
async def test_entities_comments_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/comments",
        json=[{"id": 22, "text": "Готово"}],
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_comments_list", {"entity_type": "project", "entity_id": "655f"}
        )
    assert [c.text for c in result.data] == ["Готово"]


@responses.activate
async def test_entities_comments_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/comments/22",
        json={"id": 22, "text": "hi"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_comments_get",
            {"entity_type": "project", "entity_id": "655f", "comment_id": "22"},
        )
    assert result.data.id == 22


@responses.activate
async def test_entities_links_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/links",
        json=[{"type": "relates"}],
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_links_list", {"entity_type": "project", "entity_id": "655f"}
        )
    assert [link.type for link in result.data] == ["relates"]


@responses.activate
async def test_entities_attachments_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/attachments",
        json=[{"id": "3", "name": "Shops.csv"}],
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_attachments_list", {"entity_type": "project", "entity_id": "655f"}
        )
    assert [a.name for a in result.data] == ["Shops.csv"]


@responses.activate
async def test_entities_attachments_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/entities/project/655f/attachments/5",
        json={"id": "5", "name": "flowers.jpg"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_attachments_get",
            {"entity_type": "project", "entity_id": "655f", "file_id": "5"},
        )
    assert result.data.name == "flowers.jpg"


@responses.activate
async def test_entities_bulk_status_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/656",
        json={"id": "656", "status": "COMPLETE"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool("entities_bulk_status_get", {"operation_id": "656"})
    assert result.data.status == "COMPLETE"
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == f"{BASE}/bulkchange/656"


def _comments_relative_callback(request):
    """First page → one comment, second page (from set) empty, so the drain terminates."""
    from urllib.parse import parse_qs, urlparse

    if "from" in parse_qs(urlparse(request.url).query):
        return (200, {}, '{"comments": [], "hasNext": false}')
    return (200, {}, '{"comments": [{"id": 22, "text": "hi"}], "hasNext": true}')


@responses.activate
async def test_entities_comments_relative_list_tool(creds):
    responses.add_callback(
        responses.GET,
        f"{BASE}/entities/project/655f/comments/_relative",
        callback=_comments_relative_callback,
        content_type="application/json",
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_comments_relative_list",
            {"entity_type": "project", "entity_id": "655f", "limit": 5},
        )
    assert [c.text for c in result.data] == ["hi"]


@responses.activate
async def test_entities_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/entities/project", json={"id": "655f"}, status=201)
    body = {"fields": {"summary": "New project"}}
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool("entities_create", {"entity_type": "project", "body": body})
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/entities/project"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_edit_tool(creds):
    responses.add(responses.PATCH, f"{BASE}/entities/project/655f", json={"id": "655f"}, status=200)
    body = {"fields": {"summary": "Renamed"}}
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_edit", {"entity_type": "project", "entity_id": "655f", "body": body}
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f", status=204)
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_delete", {"entity_type": "project", "entity_id": "655f", "with_board": True}
        )
    assert result.data.ok is True and "655f" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert "withBoard" in (responses.calls[0].request.url or "")


@responses.activate
async def test_entities_set_permissions_tool(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/extendedPermissions",
        json={"acl": {"WRITE": {"roles": ["OWNER"]}}},
        status=200,
    )
    body = {"write": {"add": {"users": ["me"]}}}
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_set_permissions",
            {"entity_type": "project", "entity_id": "655f", "body": body},
        )
    assert result.structured_content["acl"]["WRITE"]["roles"] == ["OWNER"]
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_bulk_update_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/bulkchange/_update",
        json={"id": "656", "status": "CREATED"},
        status=201,
    )
    body = {"metaEntities": ["655f"], "values": {"fields": {"entityStatus": "in_progress"}}}
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_bulk_update", {"entity_type": "project", "body": body}
        )
    assert result.data.status == "CREATED"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/bulkchange/_update"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_create_report_tool(creds):
    responses.add(responses.POST, f"{BASE}/entities/report/", json={"id": "r1"}, status=201)
    body = {
        "fields": {
            "summary": "Export",
            "parameters": {
                "type": "issueFilterExport",
                "format": "xlsx",
                "filter": {"query": "Queue: SUPPORT"},
                "fields": ["key", "summary"],
            },
        }
    }
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool("entities_create_report", {"body": body})
    assert result.data.id == "r1"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/entities/report/"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_comments_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/comments",
        json={"id": 23, "text": "hello"},
        status=201,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_comments_create",
            {"entity_type": "project", "entity_id": "655f", "body": {"text": "hello"}},
        )
    assert result.data.text == "hello"
    assert responses.calls[0].request.method == "POST"
    assert json.loads(responses.calls[0].request.body) == {"text": "hello"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_comments_edit_tool_patches_per_comment_route(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/comments/23",
        json={"id": 23, "text": "edited"},
        status=200,
    )
    body = {"text": "edited"}
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_comments_edit",
            {"entity_type": "project", "entity_id": "655f", "comment_id": "23", "body": body},
        )
    assert result.data.text == "edited"
    assert responses.calls[0].request.method == "PATCH"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/comments/23"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_comments_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/comments/23", status=204)
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_comments_delete",
            {"entity_type": "project", "entity_id": "655f", "comment_id": "23"},
        )
    assert result.data.ok is True and "23" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/comments/23"


@responses.activate
async def test_entities_checklists_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f"},
        status=201,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_checklists_create",
            {"entity_type": "project", "entity_id": "655f", "body": [{"text": "step 1"}]},
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "POST"
    assert json.loads(responses.calls[0].request.body) == [{"text": "step 1"}]  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_checklists_edit_tool(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f"},
        status=200,
    )
    body = [{"id": "5f", "text": "step 1", "checked": True}]
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_checklists_edit",
            {"entity_type": "project", "entity_id": "655f", "body": body},
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_checklists_edit_item_tool(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/entities/project/655f/checklistItems/5f",
        json={"id": "655f"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_checklists_edit_item",
            {
                "entity_type": "project",
                "entity_id": "655f",
                "item_id": "5f",
                "body": {"checked": True},
            },
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"checked": True}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_checklists_delete_tool(creds):
    responses.add(
        responses.DELETE,
        f"{BASE}/entities/project/655f/checklistItems",
        json={"id": "655f"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_checklists_delete", {"entity_type": "project", "entity_id": "655f"}
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/checklistItems"


@responses.activate
async def test_entities_checklists_delete_item_tool(creds):
    responses.add(
        responses.DELETE,
        f"{BASE}/entities/project/655f/checklistItems/5f",
        json={"id": "655f"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_checklists_delete_item",
            {"entity_type": "project", "entity_id": "655f", "item_id": "5f"},
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/checklistItems/5f"


@responses.activate
async def test_entities_checklists_move_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/checklistItems/5f/_move",
        json={"id": "655f"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_checklists_move",
            {
                "entity_type": "project",
                "entity_id": "655f",
                "item_id": "5f",
                "body": {"before": "6a"},
            },
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "POST"
    assert json.loads(responses.calls[0].request.body) == {"before": "6a"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_links_create_tool_returns_ack(creds):
    responses.add(responses.POST, f"{BASE}/entities/project/655f/links", status=200)
    body = {"relationship": "relates", "entity": "658"}
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_links_create",
            {"entity_type": "project", "entity_id": "655f", "body": body},
        )
    # Assert the richer unified form (target + relationship) — proves the MCP surface no
    # longer emits the old lossy `linked {type} {id}` string.
    assert result.data.ok is True
    assert "655f" in result.data.detail and "-> 658 (relates)" in result.data.detail
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/links"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_entities_links_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/links?right=658", status=200)
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_links_delete",
            {"entity_type": "project", "entity_id": "655f", "right": "658"},
        )
    assert result.data.ok is True and "658" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert "right=658" in (responses.calls[0].request.url or "")


@responses.activate
async def test_entities_attachments_attach_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/entities/project/655f/attachments/tmp1",
        json={"id": "655f"},
        status=200,
    )
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_attachments_attach",
            {"entity_type": "project", "entity_id": "655f", "temp_file_id": "tmp1"},
        )
    assert result.data.id == "655f"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/attachments/tmp1"


@responses.activate
async def test_entities_attachments_delete_tool_returns_ack_on_empty_body(creds):
    # The live API answers 200 with an EMPTY body — parsing it as JSON crashed (regression).
    responses.add(responses.DELETE, f"{BASE}/entities/project/655f/attachments/5", status=200)
    async with Client(entities_mcp.mcp) as client:
        result = await client.call_tool(
            "entities_attachments_delete",
            {"entity_type": "project", "entity_id": "655f", "file_id": "5"},
        )
    assert result.data.ok is True and "5" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/entities/project/655f/attachments/5"
