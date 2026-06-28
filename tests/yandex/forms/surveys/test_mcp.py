"""TDD for forms surveys MCP subserver — @cache factory, env+responses pattern."""
import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.forms.surveys import mcp as surveys_mcp

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_surveys_list_tool_returns_flat_collection(creds):
    responses.add(responses.GET, f"{BASE}/surveys",
                  json={"links": {}, "result": [{"id": "a"}, {"id": "b"}]}, status=200)
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_list", {})
    assert [s.id for s in result.data] == ["a", "b"]


@responses.activate
async def test_surveys_get_tool(creds):
    responses.add(responses.GET, f"{BASE}/surveys/{SID}", json={"id": SID, "name": "F"}, status=200)
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_get", {"survey_id": SID})
    assert result.data.id == SID


@responses.activate
async def test_surveys_get_not_found_is_clean_error(creds):
    responses.add(responses.GET, f"{BASE}/surveys/badid", json={"errors": {}}, status=404)
    async with Client(surveys_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("surveys_get", {"survey_id": "badid"})


@responses.activate
async def test_surveys_get_empty_response_guard(creds):
    """200 with empty body hits the id-is-None guard (blank object instead of 404)."""
    responses.add(responses.GET, f"{BASE}/surveys/{SID}", json={}, status=200)
    async with Client(surveys_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("surveys_get", {"survey_id": SID})


async def test_surveys_tools_registered_read_only():
    async with Client(surveys_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"surveys_list", "surveys_get"}
    assert tools["surveys_list"].annotations.readOnlyHint is True
