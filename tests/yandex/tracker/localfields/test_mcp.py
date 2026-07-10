"""TDD for the tracker localfields MCP subserver — fastmcp Client against the resource server."""

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.tracker.localfields import mcp as localfields_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_localfields_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields",
        json=[{"key": "a"}, {"key": "b"}],
        status=200,
    )
    async with Client(localfields_mcp.mcp) as client:
        result = await client.call_tool("localfields_list", {"queue_id": "ORG"})
    assert [f.key for f in result.data] == ["a", "b"]


@responses.activate
async def test_localfields_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/queues/ORG/localFields/k",
        json={"key": "k", "name": "Loc field", "schema": {"type": "string"}},
        status=200,
    )
    async with Client(localfields_mcp.mcp) as client:
        result = await client.call_tool("localfields_get", {"queue_id": "ORG", "field_key": "k"})
    assert result.data.key == "k" and result.data.name == "Loc field"


@responses.activate
async def test_localfields_get_empty_response_guard(creds):
    responses.add(responses.GET, f"{BASE}/queues/ORG/localFields/nope", json={}, status=200)
    async with Client(localfields_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("localfields_get", {"queue_id": "ORG", "field_key": "nope"})


@responses.activate
async def test_localfields_get_not_found_is_clean_error(creds):
    responses.add(
        responses.GET, f"{BASE}/queues/ORG/localFields/nope", json={"errors": {}}, status=404
    )
    async with Client(localfields_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("localfields_get", {"queue_id": "ORG", "field_key": "nope"})


async def test_localfields_tools_registered_read_only():
    async with Client(localfields_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"localfields_list", "localfields_get"}
    assert tools["localfields_list"].annotations.readOnlyHint is True
    assert tools["localfields_get"].annotations.readOnlyHint is True
