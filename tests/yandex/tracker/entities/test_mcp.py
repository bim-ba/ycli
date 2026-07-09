"""TDD for the tracker entities MCP subserver — read tools only, read-only hints.

The ``call_tool`` tests exercise ``client.entities.*`` through a real ``TrackerClient``; they go
green once the integrator wires ``self.entities = EntitiesClient(...)`` onto ``TrackerClient``.
The tool-shape tests (names, read-only hints) need no wiring.
"""

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
    "entities_links_list",
    "entities_attachments_list",
    "entities_attachments_get",
}


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


async def test_exposes_exactly_the_read_tools():
    async with Client(entities_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == READ_TOOLS


async def test_all_tools_are_read_only():
    async with Client(entities_mcp.mcp) as client:
        tools = await client.list_tools()
    for tool in tools:
        assert tool.annotations.readOnlyHint is True, tool.name


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
