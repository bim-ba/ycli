"""TDD for the tracker users MCP subserver (fastmcp Client against the resource subserver)."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.users import mcp as users_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_users_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/users/username",
        json={"uid": 12, "login": "username", "display": "Ivan"},
        status=200,
    )
    async with Client(users_mcp.mcp) as client:
        result = await client.call_tool("users_get", {"login_or_id": "username"})
    assert result.data.login == "username" and result.data.uid == 12


@responses.activate
async def test_users_list_tool_returns_flat_list(creds):
    responses.add(
        responses.GET,
        f"{BASE}/users/_relative",
        json={"users": [{"uid": 1, "login": "a"}, {"uid": 2, "login": "b"}], "hasNext": False},
        status=200,
    )
    async with Client(users_mcp.mcp) as client:
        result = await client.call_tool("users_list", {"limit": 2})
    assert [u.login for u in result.data] == ["a", "b"]


async def test_user_tools_registered_read_only():
    async with Client(users_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"users_get", "users_list"} <= set(tools)
    assert tools["users_get"].annotations.readOnlyHint is True
    assert tools["users_list"].annotations.readOnlyHint is True
