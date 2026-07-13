"""Wiki /pages/{id}/comments FastMCP subserver tests — write tools (ARCH-3 honesty)."""

import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import WIKI_BASE as BASE
from ycli.yandex.wiki.comments import mcp as comments_mcp

pytestmark = pytest.mark.integration


@responses.activate
async def test_comments_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/comments",
        json={"id": 678, "body": "LGTM", "parent_id": 7},
        status=200,
    )
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool(
            "comments_create", {"page_id": 42, "body": {"body": "LGTM", "parent_id": 7}}
        )
    assert result.data.id == 678
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"body": "LGTM", "parent_id": 7}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_comments_delete_tool(creds):
    responses.add(
        responses.DELETE,
        f"{BASE}/pages/42/comments/678",
        json={"comments_count": 4},
        status=200,
    )
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool("comments_delete", {"page_id": 42, "comment_id": 678})
    assert result.data.comments_count == 4
    request = responses.calls[0].request
    assert request.method == "DELETE"
    assert request.url.endswith("/pages/42/comments/678")  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize(
    ("tool_name", "destructive", "idempotent"),
    [
        ("comments_create", False, False),
        ("comments_delete", True, False),
    ],
)
async def test_comments_write_tools_carry_honest_hints(tool_name, destructive, idempotent):
    async with Client(comments_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    annotations = tools[tool_name].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is destructive
    assert annotations.idempotentHint is idempotent
    assert annotations.title
