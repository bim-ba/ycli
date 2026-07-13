"""TDD for the tracker remotelinks MCP subserver — reads + writes with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.remotelinks import mcp as remotelinks_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_remotelinks_list_tool_returns_data(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/remotelinks",
        json=[{"id": 51, "object": {"key": "TEST-17"}}],
        status=200,
    )
    async with Client(remotelinks_mcp.mcp) as client:
        result = await client.call_tool("remotelinks_list", {"issue_key": "JUNE-2"})
    assert [link.object.key for link in result.data] == ["TEST-17"]


async def test_all_remotelink_tools_exposed():
    async with Client(remotelinks_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert names == {"remotelinks_list", "remotelinks_create", "remotelinks_delete"}


async def test_list_tool_is_read_only():
    async with Client(remotelinks_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["remotelinks_list"].annotations.readOnlyHint is True


@responses.activate
async def test_remotelinks_create_tool_sends_backlink(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/remotelinks",
        json={"id": 52, "object": {"key": "EXT-1"}},
        status=201,
    )
    body = {"origin": "com.external.app", "relationship": "relates", "key": "EXT-1"}
    async with Client(remotelinks_mcp.mcp) as client:
        result = await client.call_tool(
            "remotelinks_create", {"issue_key": "JUNE-2", "body": body, "backlink": "true"}
        )
    assert result.data.object.key == "EXT-1"
    assert responses.calls[0].request.method == "POST"
    assert "backlink=true" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_remotelinks_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/issues/JUNE-2/remotelinks/52", status=204)
    async with Client(remotelinks_mcp.mcp) as client:
        result = await client.call_tool(
            "remotelinks_delete", {"issue_key": "JUNE-2", "link_id": "52"}
        )
    assert result.data.ok is True and "52" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/issues/JUNE-2/remotelinks/52"


async def test_remotelink_write_tools_annotations():
    async with Client(remotelinks_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "remotelinks_create": (False, False),
        "remotelinks_delete": (True, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
