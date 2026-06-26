"""TDD for tracker issues MCP subserver — Depends DI, RootModel return, in-memory client."""
import pytest
import requests
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues import mcp as issues_mcp

BASE = "https://api.tracker.yandex.net/v3"


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


@responses.activate
async def test_issues_get_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1", json={"key": "DE-1", "summary": "S"}, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_get", {"key": "DE-1"})
    assert result.data.key == "DE-1"


@responses.activate
async def test_issues_list_tool_returns_rootmodel(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/_search", json=[{"key": "DE-1"}, {"key": "DE-2"}], status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_list", {"queue": "DE"})
    assert [i.key for i in result.data] == ["DE-1", "DE-2"]


async def test_issue_tools_registered_read_only():
    async with Client(issues_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"issues_get", "issues_full", "issues_list", "issues_search", "issues_count"} <= set(tools)
    assert tools["issues_get"].annotations.readOnlyHint is True


@responses.activate
async def test_issues_get_tool_not_found_raises(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    # 404 error body — uplink deserializes it into an empty Issue (key=None); the tool must raise.
    responses.add(responses.GET, f"{BASE}/issues/NOPE-1",
                  json={"statusCode": 404, "errorMessages": ["Not found"]}, status=404)
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("issues_get", {"key": "NOPE-1"})


@responses.activate
async def test_issues_full_tool_returns_raw_dict(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1",
                  json={"key": "DE-1", "summary": "S", "extra": "kept"}, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_full", {"key": "DE-1"})
    assert result.data["key"] == "DE-1"
    assert result.data["extra"] == "kept"


@responses.activate
async def test_issues_search_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/_search", json=[{"key": "DE-1"}], status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_search", {"query": "Queue: DE"})
    assert [i.key for i in result.data] == ["DE-1"]


@responses.activate
async def test_issues_count_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.POST, f"{BASE}/issues/_count", json=42, status=200)
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_count", {"query": "Queue: DE"})
    assert result.data == 42
