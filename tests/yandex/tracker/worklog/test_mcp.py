"""TDD for the tracker worklog MCP subserver — reads + writes with honest annotations."""

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


def _worklog_page_callback(request):
    """Two-page drain: page 1 (no id) → id=6 empty page terminates."""
    if "id=" in request.url:
        return (200, {}, json.dumps([]))
    return (200, {}, json.dumps([{"id": 5, "duration": "PT2H"}, {"id": 6, "duration": "PT1H"}]))


@responses.activate
async def test_worklog_list_tool_drains_pages(creds):
    responses.add_callback(
        responses.GET,
        f"{BASE}/issues/DE-1/worklog",
        callback=_worklog_page_callback,
        content_type="application/json",
    )
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool("worklog_list", {"key": "DE-1"})
    assert [w.duration for w in result.data] == ["PT2H", "PT1H"]  # both pages, joined in order
    assert len(responses.calls) == 2  # page 1 + the id=6 empty page


@responses.activate
async def test_worklog_list_tool_caps_with_explicit_limit(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/worklog",
        json=[{"id": 5, "duration": "PT2H"}, {"id": 6, "duration": "PT1H"}],
        status=200,
    )
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool("worklog_list", {"key": "DE-1", "limit": 1})
    assert [w.duration for w in result.data] == ["PT2H"]  # limit forwarded through the tool
    assert len(responses.calls) == 1


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


async def test_all_worklog_tools_exposed():
    async with Client(worklog_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {
        "worklog_list",
        "worklog_search",
        "worklog_global_list",
        "worklog_create",
        "worklog_edit",
        "worklog_delete",
    }


async def test_read_tools_are_read_only():
    async with Client(worklog_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["worklog_list"].annotations.readOnlyHint is True
    assert tools["worklog_search"].annotations.readOnlyHint is True
    assert tools["worklog_global_list"].annotations.readOnlyHint is True


@responses.activate
async def test_worklog_global_list_tool(creds):
    responses.add(
        responses.GET, f"{BASE}/worklog", json=[{"id": 2, "duration": "PT1H"}], status=200
    )
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool("worklog_global_list", {"created_by": "veikus"})
    assert [w.duration for w in result.data] == ["PT1H"]
    assert responses.calls[0].request.method == "GET"
    assert "createdBy=veikus" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]


@responses.activate
async def test_worklog_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/worklog",
        json={"id": 6, "duration": "PT2H"},
        status=201,
    )
    body = {"start": "2026-07-12T10:00:00.000+0000", "duration": "PT2H"}
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool("worklog_create", {"key": "DE-1", "body": body})
    assert result.data.duration == "PT2H"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/worklog"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_worklog_edit_tool(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/issues/DE-1/worklog/6",
        json={"id": 6, "duration": "PT1H30M"},
        status=200,
    )
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool(
            "worklog_edit", {"key": "DE-1", "record_id": "6", "body": {"duration": "PT1H30M"}}
        )
    assert result.data.duration == "PT1H30M"
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == {"duration": "PT1H30M"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_worklog_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/worklog/6", status=204)
    async with Client(worklog_mcp.mcp) as client:
        result = await client.call_tool("worklog_delete", {"key": "DE-1", "record_id": "6"})
    assert result.data.ok is True and "6" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/worklog/6"


async def test_worklog_write_tools_annotations():
    async with Client(worklog_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "worklog_create": (False, False),
        "worklog_edit": (False, True),
        "worklog_delete": (True, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
