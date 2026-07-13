"""Wiki /upload_sessions FastMCP subserver tests — the ``get`` read plus the pipeline writes."""

import base64
import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import WIKI_BASE as BASE
from ycli.yandex.wiki.uploadsessions import mcp as uploadsessions_mcp

pytestmark = pytest.mark.integration


@responses.activate
async def test_uploadsessions_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/upload_sessions/s-1",
        json={"session_id": "s-1", "status": "in_progress"},
        status=200,
    )
    async with Client(uploadsessions_mcp.mcp) as client:
        result = await client.call_tool("uploadsessions_get", {"session_id": "s-1"})
    assert result.data.session_id == "s-1"
    assert result.data.status == "in_progress"


async def test_uploadsessions_get_is_registered_and_read_only():
    async with Client(uploadsessions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "uploadsessions_get" in tools
    assert tools["uploadsessions_get"].annotations.readOnlyHint is True


@responses.activate
async def test_uploadsessions_create_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions",
        json={"session_id": "s-1", "status": "not_started"},
        status=200,
    )
    async with Client(uploadsessions_mcp.mcp) as client:
        result = await client.call_tool(
            "uploadsessions_create", {"body": {"file_name": "d.png", "file_size": 2048}}
        )
    assert result.data.session_id == "s-1"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"file_name": "d.png", "file_size": 2048}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_uploadsessions_upload_part_tool_decodes_base64_to_octet_stream(creds):
    payload = b"\x89PNG raw part bytes"
    responses.add(
        responses.PUT,
        f"{BASE}/upload_sessions/s-1/upload_part",
        json={"session_id": "s-1", "status": "in_progress"},
        status=200,
    )
    async with Client(uploadsessions_mcp.mcp) as client:
        result = await client.call_tool(
            "uploadsessions_upload_part",
            {"session_id": "s-1", "part_number": 1, "data": base64.b64encode(payload).decode()},
        )
    assert result.data.status == "in_progress"
    request = responses.calls[0].request
    assert request.method == "PUT"
    assert request.headers["Content-Type"] == "application/octet-stream"
    assert request.body == payload  # verbatim bytes on the wire — no base64 leakage
    assert request.params["part_number"] == "1"  # ty: ignore[unresolved-attribute]


@responses.activate
async def test_uploadsessions_finish_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/s-1/finish",
        json={"session_id": "s-1", "status": "finished"},
        status=200,
    )
    async with Client(uploadsessions_mcp.mcp) as client:
        result = await client.call_tool("uploadsessions_finish", {"session_id": "s-1"})
    assert result.data.status == "finished"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert request.url.endswith("/upload_sessions/s-1/finish")  # ty: ignore[unresolved-attribute]


@responses.activate
async def test_uploadsessions_abort_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/s-1/abort",
        json={"session_id": "s-1", "status": "aborted"},
        status=200,
    )
    async with Client(uploadsessions_mcp.mcp) as client:
        result = await client.call_tool("uploadsessions_abort", {"session_id": "s-1"})
    assert result.data.status == "aborted"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert request.url.endswith("/upload_sessions/s-1/abort")  # ty: ignore[unresolved-attribute]


@responses.activate
async def test_uploadsessions_abort_all_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/abort_active_uploads",
        json={"status": "ok"},
        status=200,
    )
    async with Client(uploadsessions_mcp.mcp) as client:
        result = await client.call_tool("uploadsessions_abort_all", {})
    assert result.data.status == "ok"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert request.url.endswith("/upload_sessions/abort_active_uploads")  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize(
    ("tool_name", "destructive", "idempotent"),
    [
        ("uploadsessions_create", False, False),
        ("uploadsessions_upload_part", False, False),
        ("uploadsessions_finish", False, False),
        ("uploadsessions_abort", True, False),
        ("uploadsessions_abort_all", True, False),
    ],
)
async def test_uploadsessions_write_tools_carry_honest_hints(tool_name, destructive, idempotent):
    async with Client(uploadsessions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    annotations = tools[tool_name].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is destructive
    assert annotations.idempotentHint is idempotent
    assert annotations.title
