"""TDD for the tracker worklog MCP subserver — worklog_list (per-issue) + worklog_search (org)."""

import json

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.worklog import mcp as worklog_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_worklog_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/worklog",
        json=[{"id": 5, "duration": "PT2H"}],
        status=200,
    )
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool("worklog_list", {"key": "DE-1"})
    assert [w.duration for w in result.data] == ["PT2H"]


@responses.activate
async def test_worklog_search_tool_builds_body(creds):
    responses.add(
        responses.POST, f"{BASE}/worklog/_search", json=[{"id": 1, "duration": "PT2H"}], status=200
    )
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool(
            "worklog_search",
            {"created_by": "veikus", "created_from": "2018-06-06T00:00:00"},
        )
    assert [w.duration for w in result.data] == ["PT2H"]
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "createdBy": "veikus",
        "createdAt": {"from": "2018-06-06T00:00:00"},
    }


async def test_both_read_tools_exposed():
    async with Client(worklog_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"worklog_list", "worklog_search"}


async def test_tools_are_read_only():
    async with Client(worklog_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["worklog_list"].annotations.readOnlyHint is True
    assert tools["worklog_search"].annotations.readOnlyHint is True
