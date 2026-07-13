"""TDD for the Tracker global-fields MCP subserver (fastmcp Client against the subserver)."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.fields import mcp as fields_mcp


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


@responses.activate
async def test_fields_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/fields", json={"id": "custom"}, status=201)
    body = {
        "id": "custom",
        "name": {"ru": "Кастом", "en": "Custom"},
        "category": "cat-1",
        "type": "ru.yandex.startrek.core.fields.StringFieldType",
    }
    async with Client(fields_mcp.mcp) as client:
        result = await client.call_tool("fields_create", {"body": body})
    assert result.data.id == "custom"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/fields"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_fields_edit_tool_sends_version(creds):
    responses.add(responses.PATCH, f"{BASE}/fields/custom", json={"id": "custom"}, status=200)
    async with Client(fields_mcp.mcp) as client:
        result = await client.call_tool(
            "fields_edit",
            {"field_id": "custom", "body": {"name": {"en": "Custom v2"}}, "version": 2},
        )
    assert result.data.id == "custom"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=2" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"name": {"en": "Custom v2"}}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_fields_category_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/fields/categories", json={"id": "cat-2"}, status=201)
    async with Client(fields_mcp.mcp) as client:
        result = await client.call_tool(
            "fields_category_create", {"body": {"name": {"ru": "Опс", "en": "Ops"}, "order": 400}}
        )
    assert result.data.id == "cat-2"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/fields/categories"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": {"ru": "Опс", "en": "Ops"},
        "order": 400,
    }


@responses.activate
async def test_fields_category_edit_tool_sends_version(creds):
    responses.add(
        responses.PATCH, f"{BASE}/fields/categories/cat-2", json={"id": "cat-2"}, status=200
    )
    async with Client(fields_mcp.mcp) as client:
        result = await client.call_tool(
            "fields_category_edit", {"category_id": "cat-2", "body": {"order": 500}, "version": 1}
        )
    assert result.data.id == "cat-2"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=1" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"order": 500}  # ty: ignore[invalid-argument-type]


async def test_field_write_tools_annotations():
    async with Client(fields_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "fields_create": (False, False),
        "fields_edit": (False, True),
        "fields_category_create": (False, False),
        "fields_category_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
