"""Wiki /users/me resource — client, CLI, MCP."""
import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError
from typer.testing import CliRunner

import ycli.cli as cli
from ycli.yandex.wiki.me import mcp as me_mcp_module
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.me.models import Me

ME_URL = "https://api.wiki.yandex.net/v1/users/me"
ME_BODY = {
    "username": "alice",
    "home_cluster": "homepage",
    "identity": {"uid": "1", "cloud_uid": "c1"},
    "org": {"dir_id": "d1", "collab_id": "11111111-1111-1111-1111-111111111111"},
}


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")


@responses.activate
def test_client_get_parses_me(creds):
    responses.add(responses.GET, ME_URL, json=ME_BODY, status=200)
    me = WikiClient.from_env().me.get()
    assert isinstance(me, Me)
    assert me.username == "alice"
    assert me.identity.uid == "1"
    assert me.org.dir_id == "d1"


@responses.activate
@pytest.mark.integration
def test_cli_wiki_me_get(creds):
    responses.add(responses.GET, ME_URL, json=ME_BODY, status=200)
    res = CliRunner().invoke(cli.app, ["--format", "json", "wiki", "me", "get"])
    assert res.exit_code == 0
    assert "alice" in res.stdout


@responses.activate
@pytest.mark.integration
def test_mcp_wiki_me_get(creds):
    responses.add(responses.GET, ME_URL, json=ME_BODY, status=200)
    from ycli.yandex.wiki.me.mcp import get
    result = get(client=WikiClient.from_env())
    assert result.username == "alice"


@responses.activate
@pytest.mark.integration
async def test_mcp_wiki_me_auth_guard(creds):
    responses.add(responses.GET, ME_URL, json={}, status=200)
    async with Client(me_mcp_module.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("me_get", {})
