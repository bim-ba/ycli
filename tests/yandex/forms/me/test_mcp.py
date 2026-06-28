"""TDD for forms me MCP subserver — @cache factory, env+responses pattern."""
import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.forms.me import mcp as me_mcp

BASE = "https://api.forms.yandex.net/v1"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_me_get_tool(creds):
    responses.add(responses.GET, f"{BASE}/users/me",
                  json={"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"}, status=200)
    async with Client(me_mcp.mcp) as client:
        result = await client.call_tool("me_get", {})
    assert result.data.email == "e@x"


@responses.activate
async def test_me_get_auth_failure_is_clean_error(creds):
    responses.add(responses.GET, f"{BASE}/users/me", json={"errors": {}}, status=401)
    async with Client(me_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("me_get", {})


@responses.activate
async def test_me_get_empty_response_guard(creds):
    """200 with empty body hits the id-is-None guard (blank object instead of error)."""
    responses.add(responses.GET, f"{BASE}/users/me", json={}, status=200)
    async with Client(me_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("me_get", {})


async def test_me_tool_registered_read_only():
    async with Client(me_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"me_get"}
    assert tools["me_get"].annotations.readOnlyHint is True
