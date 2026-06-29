"""status_get MCP tool — aggregates the three /me probes into one read-only report."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.status import mcp as status_mcp

TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_status_get_reports_all_valid(creds):
    responses.add(responses.GET, TRACKER_ME, json={"login": "alice"}, status=200)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    services = {s.service: s for s in result.data.services}
    assert services["tracker"].valid is True
    assert services["tracker"].me.login == "alice"
    assert services["forms"].me.email == "alice@x"


@responses.activate
async def test_status_get_marks_invalid_on_401(creds):
    responses.add(responses.GET, TRACKER_ME, status=401)
    responses.add(responses.GET, WIKI_ME, json={"username": "alice"}, status=200)
    responses.add(responses.GET, FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    services = {s.service: s for s in result.data.services}
    assert services["tracker"].valid is False
    assert services["tracker"].detail == "token invalid or expired"


async def test_status_get_is_read_only():
    async with Client(status_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "get" in tools
    assert tools["get"].annotations.readOnlyHint is True
