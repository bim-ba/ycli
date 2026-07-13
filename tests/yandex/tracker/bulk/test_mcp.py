"""TDD for the tracker bulk MCP subserver — reads + write triggers with honest annotations."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.bulk import mcp as bulk_mcp


@responses.activate
async def test_bulk_get_tool_returns_status(creds):
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab",
        json={"id": "1ab", "status": "COMPLETE"},
        status=200,
    )
    async with Client(bulk_mcp.mcp) as client:
        result = await client.call_tool("bulk_get", {"bulk_id": "1ab"})
    assert result.data.status == "COMPLETE"


@responses.activate
async def test_bulk_issues_list_tool_returns_data(creds):
    responses.add(
        responses.GET,
        f"{BASE}/bulkchange/1ab/issues",
        json=[{"issue": {"key": "TEST-1"}, "status": "FAILED"}],
        status=200,
    )
    async with Client(bulk_mcp.mcp) as client:
        result = await client.call_tool("bulk_issues_list", {"bulk_id": "1ab"})
    assert [r.issue for r in result.data] == ["TEST-1"]


async def test_all_bulk_tools_exposed():
    async with Client(bulk_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"bulk_get", "bulk_issues_list", "bulk_update", "bulk_move", "bulk_transition"}


async def test_read_tools_are_read_only():
    async with Client(bulk_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["bulk_get"].annotations.readOnlyHint is True
    assert tools["bulk_issues_list"].annotations.readOnlyHint is True


@responses.activate
async def test_bulk_update_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_update",
        json={"id": "1ab", "status": "CREATED"},
        status=201,
    )
    body = {"issues": ["DE-1", "DE-2"], "values": {"priority": "minor"}}
    async with Client(bulk_mcp.mcp) as client:
        result = await client.call_tool("bulk_update", {"body": body})
    assert result.data.status == "CREATED"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/bulkchange/_update"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_bulk_move_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_move",
        json={"id": "2cd", "status": "CREATED"},
        status=201,
    )
    body = {"queue": "TARGET", "issues": ["DE-1"]}
    async with Client(bulk_mcp.mcp) as client:
        result = await client.call_tool("bulk_move", {"body": body})
    assert result.data.id == "2cd"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/bulkchange/_move"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_bulk_transition_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/bulkchange/_transition",
        json={"id": "3ef", "status": "CREATED"},
        status=201,
    )
    body = {"transition": "close", "issues": ["DE-1"]}
    async with Client(bulk_mcp.mcp) as client:
        result = await client.call_tool("bulk_transition", {"body": body})
    assert result.data.id == "3ef"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/bulkchange/_transition"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


async def test_bulk_write_tools_annotations():
    async with Client(bulk_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "bulk_update": (False, True),
        "bulk_move": (False, False),
        "bulk_transition": (False, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
