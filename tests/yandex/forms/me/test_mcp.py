"""TDD for forms me MCP subserver — Depends DI, in-memory client, auth guard."""
import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.me import mcp as me_mcp

BASE = "https://api.forms.yandex.net/v1"


def _stub() -> FormsClient:
    return FormsClient(oauth_token="t", organization_id="o")


@responses.activate
async def test_me_get_tool(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/users/me",
                  json={"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"}, status=200)
    async with Client(me_mcp.mcp) as client:
        result = await client.call_tool("me_get", {})
    assert result.data.email == "e@x"


@responses.activate
async def test_me_get_auth_failure_is_clean_error(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/users/me", json={"errors": {}}, status=401)
    async with Client(me_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("me_get", {})


@responses.activate
async def test_me_get_empty_response_guard(monkeypatch):
    """200 with empty body hits the id-is-None guard (blank object instead of error)."""
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/users/me", json={}, status=200)
    async with Client(me_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("me_get", {})


async def test_me_tool_registered_read_only():
    async with Client(me_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"me_get"}
    assert tools["me_get"].annotations.readOnlyHint is True
