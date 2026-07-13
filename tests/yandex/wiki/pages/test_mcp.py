"""Wiki /pages FastMCP subserver tests — id-based reads + the write tools (ARCH-3 honesty)."""

import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import WIKI_BASE as BASE
from ycli.yandex.wiki.pages import mcp as pages_mcp


@responses.activate
async def test_pages_by_id_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42",
        json={"id": 42, "slug": "it", "title": "It", "content": "# Hi"},
        status=200,
    )
    async with Client(pages_mcp.mcp) as client:
        result = await client.call_tool("pages_by_id_get", {"page_id": 42, "fields": "content"})
    assert result.data.id == 42
    assert result.data.content == "# Hi"
    request = responses.calls[0].request
    assert request.method == "GET"
    assert request.params["fields"] == "content"  # ty: ignore[unresolved-attribute]


@responses.activate
async def test_pages_by_id_descendants_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/descendants",
        json={"results": [{"id": 2, "slug": "it/child"}], "next_cursor": None},
        status=200,
    )
    async with Client(pages_mcp.mcp) as client:
        result = await client.call_tool("pages_by_id_descendants", {"page_id": 42})
    assert result.data[0].slug == "it/child"
    assert responses.calls[0].request.method == "GET"


@responses.activate
async def test_pages_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/pages",
        json={"id": 42, "slug": "data/x", "title": "X"},
        status=200,
    )
    async with Client(pages_mcp.mcp) as client:
        result = await client.call_tool(
            "pages_create", {"slug": "data/x", "title": "X", "content": "# X"}
        )
    assert result.data.id == 42
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"slug": "data/x", "title": "X", "content": "# X"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_pages_update_tool_replaces_content(creds):
    responses.add(
        responses.POST,
        f"{BASE}/pages/42",
        json={"id": 42, "slug": "data/x", "title": "X"},
        status=200,
    )
    async with Client(pages_mcp.mcp) as client:
        result = await client.call_tool("pages_update", {"page_id": 42, "content": "# Updated"})
    assert result.data.id == 42
    request = responses.calls[0].request
    assert request.method == "POST"  # POST-not-PATCH quirk
    assert json.loads(request.body) == {"content": "# Updated"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_pages_update_tool_carries_optional_title(creds):
    responses.add(
        responses.POST,
        f"{BASE}/pages/42",
        json={"id": 42, "slug": "data/x", "title": "New"},
        status=200,
    )
    async with Client(pages_mcp.mcp) as client:
        await client.call_tool("pages_update", {"page_id": 42, "content": "# U", "title": "New"})
    assert json.loads(responses.calls[0].request.body) == {"content": "# U", "title": "New"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_pages_delete_tool_returns_recovery_token(creds):
    responses.add(
        responses.DELETE, f"{BASE}/pages/42", json={"recovery_token": "tok-1"}, status=200
    )
    async with Client(pages_mcp.mcp) as client:
        result = await client.call_tool("pages_delete", {"page_id": 42})
    assert result.data.recovery_token == "tok-1"
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
async def test_pages_append_content_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/append-content",
        json={"id": 42, "slug": "data/x", "title": "X"},
        status=200,
    )
    async with Client(pages_mcp.mcp) as client:
        result = await client.call_tool(
            "pages_append_content",
            {"page_id": 42, "body": {"content": "## More", "body": {"location": "bottom"}}},
        )
    assert result.data.id == 42
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"content": "## More", "body": {"location": "bottom"}}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_pages_clone_tool_returns_operation(creds):
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/clone",
        json={"operation": {"type": "clone", "id": "task-1"}},
        status=200,
    )
    async with Client(pages_mcp.mcp) as client:
        result = await client.call_tool("pages_clone", {"page_id": 42, "body": {"target": "d/y"}})
    assert result.data.operation.id == "task-1"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"target": "d/y", "subscribe_me": False}  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("tool_name", "destructive", "idempotent"),
    [
        ("pages_create", False, False),
        ("pages_update", False, True),
        ("pages_delete", True, False),
        ("pages_append_content", False, False),
        ("pages_clone", False, False),
    ],
)
async def test_pages_write_tools_carry_honest_hints(tool_name, destructive, idempotent):
    async with Client(pages_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    annotations = tools[tool_name].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is destructive
    assert annotations.idempotentHint is idempotent
    assert annotations.title


@pytest.mark.parametrize("tool_name", ["pages_by_id_get", "pages_by_id_descendants"])
async def test_pages_by_id_tools_are_read_only(tool_name):
    async with Client(pages_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools[tool_name].annotations.readOnlyHint is True
    assert tools[tool_name].annotations.title
