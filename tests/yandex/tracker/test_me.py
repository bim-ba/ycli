"""Tracker /myself resource — client + CLI + MCP, HTTP stubbed."""
from __future__ import annotations

import asyncio
import json

import pytest
import requests
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError
from typer.testing import CliRunner

import ycli.cli as cli
from ycli.mcp import mcp as root_mcp
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.me.models import Me
from ycli.yandex.tracker.me import mcp as me_mcp_module

_URL = "https://api.tracker.yandex.net/v3/myself"
_PAYLOAD = {"uid": 42, "login": "alice", "display": "Alice A.", "email": "alice@example.com"}
_runner = CliRunner()


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_me_client_get(creds):
    responses.add(responses.GET, _URL, json=_PAYLOAD, status=200)
    me = TrackerClient.from_env().me.get()
    assert isinstance(me, Me)
    assert me.login == "alice" and me.uid == 42


@responses.activate
def test_me_cli_get(creds):
    responses.add(responses.GET, _URL, json=_PAYLOAD, status=200)
    res = _runner.invoke(cli.app, ["--format", "json", "tracker", "me", "get"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["login"] == "alice"


@responses.activate
def test_me_mcp_tool(creds):
    responses.add(responses.GET, _URL, json=_PAYLOAD, status=200)

    async def go():
        async with Client(root_mcp) as client:
            return await client.call_tool("tracker_me_get", {})

    result = asyncio.run(go())
    assert result.data.login == "alice"


@responses.activate
async def test_me_mcp_auth_guard(monkeypatch):
    def _stub() -> TrackerClient:
        s = requests.Session()
        s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
        return TrackerClient(oauth_token="t", organization_id="o", session=s)

    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, _URL, json={}, status=401)
    async with Client(me_mcp_module.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("me_get", {})


@responses.activate
async def test_me_mcp_empty_response_guard(monkeypatch):
    """200 with empty body hits the login-is-None guard (e.g. bad permissions → blank object)."""
    monkeypatch.setattr(TrackerClient, "from_env", classmethod(lambda cls: TrackerClient(oauth_token="t", organization_id="o")))
    responses.add(responses.GET, _URL, json={}, status=200)
    async with Client(me_mcp_module.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("me_get", {})
