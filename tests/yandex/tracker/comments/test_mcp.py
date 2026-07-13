"""TDD for the tracker comments MCP subserver — reads + writes with honest annotations."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.comments import mcp as comments_mcp


def _comments_page_callback(request):
    """Two-page drain: page 1 (no id) → id=2 empty page terminates."""
    if "id=" in request.url:
        return (200, {}, json.dumps([]))
    return (200, {}, json.dumps([{"id": 1, "text": "hi"}, {"id": 2, "text": "again"}]))


@responses.activate
async def test_comments_list_tool_drains_pages(creds):
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/comments",
        callback=_comments_page_callback,
        content_type="application/json",
    )
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool("comments_list", {"key": "DE-1"})
    assert [c.text for c in result.data] == ["hi", "again"]  # both pages, joined in order
    assert len(responses.calls) == 2  # page 1 + the id=2 empty page


@responses.activate
async def test_comments_list_tool_caps_with_explicit_limit(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/comments",
        json=[{"id": 1, "text": "hi"}, {"id": 2, "text": "again"}],
        status=200,
    )
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool("comments_list", {"key": "DE-1", "limit": 1})
    assert [c.text for c in result.data] == ["hi"]  # limit forwarded through the tool
    assert len(responses.calls) == 1


@responses.activate
async def test_comments_add_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/issues/DE-1/comments/", json={"id": 1, "text": "hi"}, status=201
    )
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool("comments_add", {"key": "DE-1", "body": {"text": "hi"}})
    assert result.data.text == "hi"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/comments/"
    assert json.loads(responses.calls[0].request.body) == {"text": "hi"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_comments_edit_tool(creds):
    responses.add(
        responses.PATCH, f"{BASE}/issues/DE-1/comments/1", json={"id": 1, "text": "upd"}, status=200
    )
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool(
            "comments_edit", {"key": "DE-1", "comment_id": "1", "body": {"text": "upd"}}
        )
    assert result.data.text == "upd"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"text": "upd"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_comments_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/comments/1", status=204)
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool("comments_delete", {"key": "DE-1", "comment_id": "1"})
    assert result.data.ok is True and "1" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/comments/1"


@responses.activate
async def test_comments_react_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/comments/1/reactions/like",
        json={"id": 1, "text": "hi"},
        status=200,
    )
    async with Client(comments_mcp.mcp) as client:
        result = await client.call_tool(
            "comments_react", {"key": "DE-1", "comment_id": "1", "name": "like"}
        )
    assert result.data.id == 1
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/comments/1/reactions/like"


async def test_comment_tools_annotations():
    async with Client(comments_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["comments_list"].annotations.readOnlyHint is True
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "comments_add": (False, False),
        "comments_edit": (False, True),
        "comments_delete": (True, False),
        "comments_react": (False, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
