"""Tracker FastMCP domain server — 14 reads-only tools, namespaced <resource>_<action>."""
import requests
import responses
from fastmcp import Client

from ycli.yandex.tracker import mcp as tracker_mcp
from ycli.yandex.tracker.client import TrackerClient

BASE = "https://api.tracker.yandex.net/v3"


def _stub() -> TrackerClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TrackerClient(session=s)


async def test_all_fourteen_read_tools_registered():
    async with Client(tracker_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {
        "me_get",
        "issues_get", "issues_full", "issues_list", "issues_search", "issues_count",
        "comments_list", "links_list", "transitions_list", "worklog_list",
        "changelog_list", "priorities_list", "issuetypes_list", "linktypes_list",
    }


@responses.activate
async def test_priorities_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/priorities", json=[{"key": "normal"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("priorities_list", {})
    assert result.data[0].key == "normal"


@responses.activate
async def test_issuetypes_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issuetypes", json=[{"key": "task"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("issuetypes_list", {})
    assert result.data[0].key == "task"


@responses.activate
async def test_linktypes_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/linktypes", json=[{"id": "relates"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("linktypes_list", {})
    assert result.data[0].id == "relates"


@responses.activate
async def test_comments_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/comments", json=[{"text": "hi"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("comments_list", {"key": "DE-1"})
    assert result.data[0].text == "hi"


@responses.activate
async def test_links_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/links",
                  json=[{"object": {"key": "DE-2"}}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("links_list", {"key": "DE-1"})
    assert result.data[0].object.key == "DE-2"


@responses.activate
async def test_transitions_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/transitions", json=[{"id": "close"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("transitions_list", {"key": "DE-1"})
    assert result.data[0].id == "close"


@responses.activate
async def test_worklog_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/worklog", json=[{"duration": "PT2H"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("worklog_list", {"key": "DE-1"})
    assert result.data[0].duration == "PT2H"


@responses.activate
async def test_changelog_list_tool(monkeypatch):
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/issues/DE-1/changelog", json=[{"id": "1"}], status=200)
    async with Client(tracker_mcp.mcp) as client:
        result = await client.call_tool("changelog_list", {"key": "DE-1"})
    assert result.data[0].id == "1"
