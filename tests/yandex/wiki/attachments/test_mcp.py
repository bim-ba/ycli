"""Wiki /pages/{id}/attachments FastMCP subserver tests — write tools (ARCH-3 honesty)."""

import base64
import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import WIKI_BASE as BASE
from ycli.yandex.wiki.attachments import mcp as attachments_mcp


@responses.activate
async def test_attachments_attach_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"id": 678, "name": "d.png"}]},
        status=200,
    )
    async with Client(attachments_mcp.mcp) as client:
        result = await client.call_tool(
            "attachments_attach", {"page_id": 42, "session_ids": ["s-1"]}
        )
    assert result.data[0].name == "d.png"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"upload_sessions": ["s-1"]}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_attachments_upload_tool_runs_whole_pipeline(creds):
    payload = b"\x89PNG raw bytes"
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions",
        json={"session_id": "s-1", "status": "in_progress"},
        status=200,
    )
    responses.add(
        responses.PUT,
        f"{BASE}/upload_sessions/s-1/upload_part",
        json={"session_id": "s-1", "status": "in_progress"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/s-1/finish",
        json={"session_id": "s-1", "status": "finished"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"id": 678, "name": "d.png"}]},
        status=200,
    )
    async with Client(attachments_mcp.mcp) as client:
        result = await client.call_tool(
            "attachments_upload",
            {
                "page_id": 42,
                "file_name": "d.png",
                "data": base64.b64encode(payload).decode(),
            },
        )
    assert result.data[0].name == "d.png"
    create_request = responses.calls[0].request
    assert json.loads(create_request.body) == {"file_name": "d.png", "file_size": len(payload)}  # ty: ignore[invalid-argument-type]
    part_request = responses.calls[1].request
    assert part_request.body == payload  # decoded base64 → verbatim octet-stream bytes
    assert part_request.params["part_number"] == "1"  # ty: ignore[unresolved-attribute]
    attach_request = responses.calls[3].request
    assert json.loads(attach_request.body) == {"upload_sessions": ["s-1"]}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_attachments_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/pages/42/attachments/678", status=204)
    async with Client(attachments_mcp.mcp) as client:
        result = await client.call_tool("attachments_delete", {"page_id": 42, "file_id": 678})
    assert result.data.ok is True
    assert "678" in result.data.detail
    request = responses.calls[0].request
    assert request.method == "DELETE"
    assert request.url.endswith("/pages/42/attachments/678")  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize(
    ("tool_name", "destructive", "idempotent"),
    [
        ("attachments_attach", False, False),
        ("attachments_upload", False, False),
        ("attachments_delete", True, False),
    ],
)
async def test_attachments_write_tools_carry_honest_hints(tool_name, destructive, idempotent):
    async with Client(attachments_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    annotations = tools[tool_name].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is destructive
    assert annotations.idempotentHint is idempotent
    assert annotations.title
