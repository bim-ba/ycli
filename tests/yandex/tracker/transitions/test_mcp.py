"""TDD for the tracker transitions MCP subserver — reads + writes with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.transitions import mcp as transitions_mcp

pytestmark = pytest.mark.integration


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
    assert tools["transitions_list"].annotations.read_only_hint is True
    ann = tools["transitions_execute"].annotations
    assert ann.read_only_hint is False
    assert ann.destructive_hint is False
    assert ann.idempotent_hint is False
    assert ann.title
