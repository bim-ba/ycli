"""TDD for tracker issues MCP subserver — per-request provider, env + MockAPI pattern."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.issues import mcp as issues_mcp

pytestmark = pytest.mark.integration


async def test_issues_get_tool(api, creds):
    api.add("GET", f"{BASE}/issues/DE-1", json={"key": "DE-1", "summary": "S"}, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_get", {"key": "DE-1"})
    assert result.data.key == "DE-1"


async def test_issues_list_tool_returns_rootmodel(api, creds):
    api.add(
        "POST",
        f"{BASE}/issues/_search",
        json=[{"key": "DE-1"}, {"key": "DE-2"}],
        status=200,
    )
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_list", {"queue": "DE"})
    assert [i.key for i in result.data] == ["DE-1", "DE-2"]


async def test_issue_tools_registered_read_only():
    async with Client(issues_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"issues_get", "issues_list", "issues_search", "issues_count"} <= set(tools)
    assert tools["issues_get"].annotations.read_only_hint is True


async def test_issues_get_tool_not_found_raises(api, creds):
    api.add(
        "GET",
        f"{BASE}/issues/NOPE-1",
        json={"statusCode": 404, "errorMessages": ["Not found"]},
        status=404,
    )
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("issues_get", {"key": "NOPE-1"})


async def test_issues_get_tool_empty_response_guard(api, creds):
    """200 with empty body hits the key-is-None guard (e.g. bad permissions → blank object)."""
    api.add("GET", f"{BASE}/issues/DE-1", json={}, status=200)
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("issues_get", {"key": "DE-1"})


async def test_issues_search_tool(api, creds):
    api.add("POST", f"{BASE}/issues/_search", json=[{"key": "DE-1"}], status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_search", {"query": "Queue: DE"})
    assert [i.key for i in result.data] == ["DE-1"]


async def test_issues_count_tool(api, creds):
    api.add("POST", f"{BASE}/issues/_count", json=42, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_count", {"query": "Queue: DE"})
    assert result.data == 42


async def test_issues_count_tool_filter_body(api, creds):
    """MCP count tool must accept queue/status filters and forward the same filter body as CLI."""
    api.add("POST", f"{BASE}/issues/_count", json=7, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_count", {"queue": "DE", "status": "open"})
    assert result.data == 7
    sent = api.body(0)
    assert sent == {"filter": {"queue": "DE", "status": "open"}}


async def test_issues_suggest_tool(api, creds):
    api.add("GET", f"{BASE}/issues/_suggest", json=[{"key": "DE-1"}], status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_suggest", {"text": "fix"})
    assert [i.key for i in result.data] == ["DE-1"]
    assert "input=fix" in (str(api.calls[0].url) or "")


async def test_issues_create_tool(api, creds):
    api.add("POST", f"{BASE}/issues/", json={"key": "DE-3", "summary": "New"}, status=201)
    body = {"queue": "DE", "summary": "New"}
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_create", {"body": body})
    assert result.data.key == "DE-3"
    assert api.calls[0].method == "POST"
    assert str(api.calls[0].url) == f"{BASE}/issues/"
    assert api.body(0) == body


async def test_issues_update_tool(api, creds):
    api.add("PATCH", f"{BASE}/issues/DE-3", json={"key": "DE-3", "summary": "Upd"}, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool(
            "issues_update", {"key": "DE-3", "body": {"summary": "Upd"}}
        )
    assert result.data.summary == "Upd"
    assert api.calls[0].method == "PATCH"
    assert api.body(0) == {"summary": "Upd"}


async def test_issues_move_tool(api, creds):
    api.add("POST", f"{BASE}/issues/DE-3/_move", json={"key": "TGT-1"}, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_move", {"key": "DE-3", "queue": "TGT"})
    assert result.data.key == "TGT-1"
    assert api.calls[0].method == "POST"
    assert "queue=TGT" in (str(api.calls[0].url) or "")


async def test_issues_scroll_clear_tool_returns_ack(api, creds):
    api.add("POST", f"{BASE}/system/search/scroll/_clear", json={}, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_scroll_clear", {"body": {"scrollId": "token"}})
    assert result.data.ok is True
    assert api.calls[0].method == "POST"
    assert str(api.calls[0].url) == f"{BASE}/system/search/scroll/_clear"
    assert api.body(0) == {"scrollId": "token"}


async def test_issue_write_tools_annotations():
    async with Client(issues_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["issues_suggest"].annotations.read_only_hint is True
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "issues_create": (False, False),
        "issues_update": (False, True),
        "issues_move": (False, False),
        "issues_scroll_clear": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.read_only_hint is False, name
        assert ann.destructive_hint is destructive, name
        assert ann.idempotent_hint is idempotent, name
        assert ann.title, name


async def test_issues_get_404_raises_through_transport_hook(api, creds):
    """Prove the production not-found path: the per-request provider builds a real client (with the
    Transport response hook) that raises YandexNotFoundError on a 404, which FastMCP
    surfaces as a ToolError.
    """
    api.add(
        "GET",
        f"{BASE}/issues/NOPE-1",
        json={"errorMessages": ["not found"]},
        status=404,
    )
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("issues_get", {"key": "NOPE-1"})


async def test_issues_search_tool_honours_limit(api, creds):
    page = [{"key": f"DE-{n}"} for n in range(1, 101)]
    api.add("POST", f"{BASE}/issues/_search", json=page, headers={"X-Total-Pages": "4"})
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_search", {"query": "Queue: DE", "limit": 7})
    assert len(result.structured_content["result"]) == 7
