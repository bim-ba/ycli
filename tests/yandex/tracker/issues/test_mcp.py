"""TDD for tracker issues MCP subserver — @cache factory, env+responses pattern."""

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.tracker.issues import mcp as issues_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_issues_get_tool(creds):
    responses.add(
        responses.GET, f"{BASE}/issues/DE-1", json={"key": "DE-1", "summary": "S"}, status=200
    )
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_get", {"key": "DE-1"})
    assert result.data.key == "DE-1"


@responses.activate
async def test_issues_list_tool_returns_rootmodel(creds):
    responses.add(
        responses.POST,
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
    assert tools["issues_get"].annotations.readOnlyHint is True


@responses.activate
async def test_issues_get_tool_not_found_raises(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/NOPE-1",
        json={"statusCode": 404, "errorMessages": ["Not found"]},
        status=404,
    )
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("issues_get", {"key": "NOPE-1"})


@responses.activate
async def test_issues_get_tool_empty_response_guard(creds):
    """200 with empty body hits the key-is-None guard (e.g. bad permissions → blank object)."""
    responses.add(responses.GET, f"{BASE}/issues/DE-1", json={}, status=200)
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("issues_get", {"key": "DE-1"})


@responses.activate
async def test_issues_search_tool(creds):
    responses.add(responses.POST, f"{BASE}/issues/_search", json=[{"key": "DE-1"}], status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_search", {"query": "Queue: DE"})
    assert [i.key for i in result.data] == ["DE-1"]


@responses.activate
async def test_issues_count_tool(creds):
    responses.add(responses.POST, f"{BASE}/issues/_count", json=42, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_count", {"query": "Queue: DE"})
    assert result.data == 42


@responses.activate
async def test_issues_count_tool_filter_body(creds):
    """MCP count tool must accept queue/status filters and forward the same filter body as CLI."""
    import json as _json

    responses.add(responses.POST, f"{BASE}/issues/_count", json=7, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_count", {"queue": "DE", "status": "open"})
    assert result.data == 7
    sent = _json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"filter": {"queue": "DE", "status": "open"}}


@pytest.mark.integration
@responses.activate
async def test_issues_get_404_raises_through_transport_hook(creds):
    """Prove the production not-found path: the @cache factory builds a real client (with the
    Transport response hook) that raises YandexNotFoundError on a 404, which FastMCP
    surfaces as a ToolError.
    """
    responses.add(
        responses.GET,
        f"{BASE}/issues/NOPE-1",
        json={"errorMessages": ["not found"]},
        status=404,
    )
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("issues_get", {"key": "NOPE-1"})
