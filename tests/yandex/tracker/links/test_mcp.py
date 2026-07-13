"""TDD for the tracker links MCP subserver — reads + writes with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.links import mcp as links_mcp

pytestmark = pytest.mark.integration


@responses.activate
async def test_links_add_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/links",
        json={"id": 1, "object": {"key": "DE-2"}},
        status=201,
    )
    async with Client(links_mcp.mcp) as client:
        result = await client.call_tool(
            "links_add", {"key": "DE-1", "body": {"relationship": "relates", "issue": "DE-2"}}
        )
    assert result.data.object.key == "DE-2"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/links"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "relationship": "relates",
        "issue": "DE-2",
    }


@responses.activate
async def test_links_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/issues/DE-1/links/1", status=204)
    async with Client(links_mcp.mcp) as client:
        result = await client.call_tool("links_delete", {"key": "DE-1", "link_id": "1"})
    assert result.data.ok is True and "1" in result.data.detail
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url == f"{BASE}/issues/DE-1/links/1"


async def test_link_tools_annotations():
    async with Client(links_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["links_list"].annotations.readOnlyHint is True
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "links_add": (False, False),
        "links_delete": (True, False),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
