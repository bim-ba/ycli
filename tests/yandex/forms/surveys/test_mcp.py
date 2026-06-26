"""TDD for forms surveys MCP subserver — list envelope + get guard."""
import pytest
import requests
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.surveys import mcp as surveys_mcp

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _stub() -> FormsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return FormsClient(session=s)


@responses.activate
async def test_surveys_list_tool_returns_envelope(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys",
                  json={"links": {}, "result": [{"id": "a"}, {"id": "b"}]}, status=200)
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_list", {})
    assert [s.id for s in result.data.result] == ["a", "b"]


@responses.activate
async def test_surveys_get_tool(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys/{SID}", json={"id": SID, "name": "F"}, status=200)
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_get", {"survey_id": SID})
    assert result.data.id == SID


@responses.activate
async def test_surveys_get_not_found_is_clean_error(monkeypatch):
    monkeypatch.setattr(FormsClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(responses.GET, f"{BASE}/surveys/badid", json={"errors": {}}, status=404)
    async with Client(surveys_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("surveys_get", {"survey_id": "badid"})


async def test_surveys_tools_registered_read_only():
    async with Client(surveys_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"surveys_list", "surveys_get"}
    assert tools["surveys_list"].annotations.readOnlyHint is True
