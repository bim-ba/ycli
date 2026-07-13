"""TDD for the tracker localfields MCP subserver — fastmcp Client against the resource server."""

import json

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.localfields import mcp as localfields_mcp


@responses.activate
async def test_localfields_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields",
        json=[{"key": "a"}, {"key": "b"}],
        status=200,
    )
    async with Client(localfields_mcp.mcp) as client:
        result = await client.call_tool("localfields_list", {"queue_id": "ORG"})
    assert [f.key for f in result.data] == ["a", "b"]


@responses.activate
async def test_localfields_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields/k",
        json={"key": "k", "name": "Loc field", "schema": {"type": "string"}},
        status=200,
    )
    async with Client(localfields_mcp.mcp) as client:
        result = await client.call_tool("localfields_get", {"queue_id": "ORG", "field_key": "k"})
    assert result.data.key == "k" and result.data.name == "Loc field"


@responses.activate
async def test_localfields_get_empty_response_guard(creds):
    responses.add(responses.GET, f"{BASE}/queues/ORG/localFields/nope", json={}, status=200)
    async with Client(localfields_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("localfields_get", {"queue_id": "ORG", "field_key": "nope"})


@responses.activate
async def test_localfields_get_not_found_is_clean_error(creds):
    responses.add(
        responses.GET, f"{BASE}/queues/ORG/localFields/nope", json={"errors": {}}, status=404
    )
    async with Client(localfields_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("localfields_get", {"queue_id": "ORG", "field_key": "nope"})


async def test_localfields_tools_registered():
    async with Client(localfields_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "localfields_list",
        "localfields_get",
        "localfields_create",
        "localfields_edit",
    }
    assert tools["localfields_list"].annotations.readOnlyHint is True
    assert tools["localfields_get"].annotations.readOnlyHint is True


@responses.activate
async def test_localfields_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/queues/ORG/localFields", json={"key": "custom"}, status=201
    )
    body = {
        "id": "custom",
        "name": {"ru": "Кастом", "en": "Custom"},
        "category": "cat-1",
        "type": "ru.yandex.startrek.core.fields.StringFieldType",
    }
    async with Client(localfields_mcp.mcp) as client:
        result = await client.call_tool("localfields_create", {"queue_id": "ORG", "body": body})
    assert result.data.key == "custom"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/queues/ORG/localFields"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_localfields_edit_tool(creds):
    responses.add(
        responses.PATCH, f"{BASE}/queues/ORG/localFields/custom", json={"key": "custom"}, status=200
    )
    async with Client(localfields_mcp.mcp) as client:
        result = await client.call_tool(
            "localfields_edit",
            {"queue_id": "ORG", "field_key": "custom", "body": {"description": "renamed"}},
        )
    assert result.data.key == "custom"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"description": "renamed"}  # ty: ignore[invalid-argument-type]


async def test_localfield_write_tools_annotations():
    async with Client(localfields_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "localfields_create": (False, False),
        "localfields_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
