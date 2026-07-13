"""TDD for the tracker transitions MCP subserver — reads + writes with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.transitions import mcp as transitions_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_transitions_execute_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/transitions/close/_execute",
        json=[{"id": "reopen"}],
        status=200,
    )
    async with Client(transitions_mcp.mcp) as client:
        result = await client.call_tool(
            "transitions_execute",
            {"key": "DE-1", "transition_id": "close", "body": {"resolution": "fixed"}},
        )
    assert result.data[0].id == "reopen"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/transitions/close/_execute"
    assert json.loads(responses.calls[0].request.body) == {"resolution": "fixed"}  # ty: ignore[invalid-argument-type]


async def test_transition_tools_annotations():
    async with Client(transitions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["transitions_list"].annotations.readOnlyHint is True
    ann = tools["transitions_execute"].annotations
    assert ann.readOnlyHint is False
    assert ann.destructiveHint is False
    assert ann.idempotentHint is False
    assert ann.title
