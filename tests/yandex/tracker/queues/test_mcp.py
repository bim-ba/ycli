"""TDD for the tracker queues MCP subserver — fastmcp Client against the resource server."""

import json

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.queues import mcp as queues_mcp


@responses.activate
async def test_queues_list_tool_returns_flat_collection(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"id": "3", "key": "TEST"}, {"id": "4", "key": "DEMO"}],
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_list", {})
    assert [q.key for q in result.data] == ["TEST", "DEMO"]


@responses.activate
async def test_queues_list_tool_honours_limit(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/",
        json=[{"key": "A"}, {"key": "B"}, {"key": "C"}],
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_list", {"limit": 1})
    assert [q.key for q in result.data] == ["A"]


@responses.activate
async def test_queues_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST",
        json={"id": "3", "key": "TEST", "name": "Test"},
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_get", {"queue_id": "TEST"})
    assert result.data.key == "TEST" and result.data.name == "Test"


@responses.activate
async def test_queues_get_empty_response_guard(creds):
    """200 with an empty body trips the not-found guard rather than returning a blank queue."""
    responses.add(responses.GET, f"{BASE}/queues/NOPE", json={}, status=200)
    async with Client(queues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("queues_get", {"queue_id": "NOPE"})


@responses.activate
async def test_queues_get_not_found_is_clean_error(creds):
    responses.add(responses.GET, f"{BASE}/queues/NOPE", json={"errors": {}}, status=404)
    async with Client(queues_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("queues_get", {"queue_id": "NOPE"})


@responses.activate
async def test_queues_tags_list_tool(creds):
    responses.add(responses.GET, f"{BASE}/queues/TEST/tags", json=["tag1", "tag2"], status=200)
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_tags_list", {"queue_id": "TEST"})
    assert result.data == ["tag1", "tag2"]


@responses.activate
async def test_queues_versions_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/versions",
        json=[{"id": 1, "name": "v0.1"}],
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_versions_list", {"queue_id": "TEST"})
    assert result.data[0].name == "v0.1"


@responses.activate
async def test_queues_fields_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/TEST/fields",
        json=[{"id": "myfield", "name": "My field"}],
        status=200,
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_fields_list", {"queue_id": "TEST"})
    assert result.data[0].id == "myfield"


async def test_queues_tools_registered():
    async with Client(queues_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    read_tools = {
        "queues_list",
        "queues_get",
        "queues_tags_list",
        "queues_versions_list",
        "queues_fields_list",
    }
    write_tools = {
        "queues_create",
        "queues_delete",
        "queues_restore",
        "queues_set_permissions",
        "queues_tag_remove",
        "queues_version_create",
    }
    assert set(tools) == read_tools | write_tools
    assert all(tools[name].annotations.readOnlyHint is True for name in read_tools)


@responses.activate
async def test_queues_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/queues/", json={"id": "9", "key": "TST"}, status=201)
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool(
            "queues_create",
            {
                "body": {
                    "key": "TST",
                    "name": "Test queue",
                    "lead": "me",
                    "default_type": "task",
                    "default_priority": "normal",
                }
            },
        )
    assert result.data.key == "TST"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/queues/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "key": "TST",
        "name": "Test queue",
        "lead": "me",
        "defaultType": "task",
        "defaultPriority": "normal",
    }


@responses.activate
async def test_queues_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/queues/TST", status=204)
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_delete", {"queue_id": "TST"})
    assert result.data.ok is True and "TST" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/queues/TST"


@responses.activate
async def test_queues_restore_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/queues/TST/_restore", json={"id": "9", "key": "TST"}, status=200
    )
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_restore", {"queue_id": "TST"})
    assert result.data.key == "TST"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/queues/TST/_restore"


@responses.activate
async def test_queues_set_permissions_tool(creds):
    responses.add(
        responses.PATCH, f"{BASE}/queues/TST/permissions", json={"version": 11}, status=200
    )
    body = {"write": {"users": {"add": ["me"]}}}
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool("queues_set_permissions", {"queue_id": "TST", "body": body})
    assert result.data.version == 11
    assert responses.calls[0].request.method == "PATCH"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_queues_tag_remove_tool_returns_ack(creds):
    responses.add(responses.POST, f"{BASE}/queues/TST/tags/_remove", status=200)
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool(
            "queues_tag_remove", {"queue_id": "TST", "body": {"tag": "old"}}
        )
    assert result.data.ok is True and "old" in result.data.detail
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/queues/TST/tags/_remove"
    assert json.loads(responses.calls[0].request.body) == {"tag": "old"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_queues_version_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/versions/", json={"id": 5, "name": "v1"}, status=201)
    async with Client(queues_mcp.mcp) as client:
        result = await client.call_tool(
            "queues_version_create", {"body": {"queue": "TST", "name": "v1"}}
        )
    assert result.data.name == "v1"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/versions/"
    assert json.loads(responses.calls[0].request.body) == {"queue": "TST", "name": "v1"}  # ty: ignore[invalid-argument-type]


async def test_queue_write_tools_annotations():
    async with Client(queues_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "queues_create": (False, False),
        "queues_delete": (True, False),
        "queues_restore": (False, False),
        "queues_set_permissions": (False, True),
        "queues_tag_remove": (True, False),
        "queues_version_create": (False, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
