"""status_get MCP tool — one read-only report: the owner, the organization, each service."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.status import mcp as status_mcp

ID_URL = "https://login.yandex.ru/info"
ORG_URL = "https://api360.yandex.net/directory/v1/org"
TRACKER_ME = "https://api.tracker.yandex.net/v3/myself"
FORMS_ME = "https://api.forms.yandex.net/v1/users/me"
WIKI_ME = "https://api.wiki.yandex.net/v1/users/me"


async def test_status_get_reports_the_owner_the_organization_and_every_service(api, monkeypatch):
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "42")
    api.add("GET", ID_URL, json={"id": "7", "login": "alice", "display_name": "Alice"})
    api.add("GET", ORG_URL, json={"organizations": [{"id": 42, "name": "Acme"}]})
    api.add("GET", TRACKER_ME, json={"login": "alice"}, status=200)
    api.add("GET", WIKI_ME, json={"username": "alice"}, status=200)
    api.add("GET", FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    report = result.data
    assert report.configured is True
    assert (report.identity.login, report.identity.display_name) == ("alice", "Alice")
    assert (report.organization.id, report.organization.name) == ("42", "Acme")
    assert {s.service: s.valid for s in report.services} == {
        "tracker": True,
        "wiki": True,
        "forms": True,
    }


async def test_status_get_marks_invalid_on_401(api, monkeypatch):
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "42")
    api.add("GET", ID_URL, json={"id": "7", "login": "alice"})
    api.add("GET", ORG_URL, json={"organizations": []})
    api.add("GET", TRACKER_ME, status=401)
    api.add("GET", WIKI_ME, json={"username": "alice"}, status=200)
    api.add("GET", FORMS_ME, json={"id": 1, "email": "alice@x"}, status=200)
    async with Client(status_mcp.mcp) as client:
        result = await client.call_tool("get", {})
    services = {s.service: s for s in result.data.services}
    assert services["tracker"].valid is False
    assert services["tracker"].detail == "token invalid or expired"


async def test_status_get_without_credentials_names_the_missing_variables(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    async with Client(status_mcp.mcp) as client:
        with pytest.raises(ToolError, match="YANDEX_ID_OAUTH_TOKEN, YANDEX_ID_ORGANIZATION_ID"):
            await client.call_tool("get", {})


async def test_status_get_is_read_only():
    async with Client(status_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "get" in tools
    assert tools["get"].annotations.read_only_hint is True


async def test_status_get_is_annotated_as_a_read():
    """status_get is the one tool outside a resource, so the contract test does not see it."""
    from ycli.yandex.mcp import RO

    async with Client(status_mcp.mcp) as client:
        tool = next(tool for tool in await client.list_tools() if tool.name == "get")
    hints = tool.annotations.model_dump(by_alias=True) if tool.annotations else {}
    assert {key: hints.get(key) for key in RO} == RO
