"""TDD for forms answers MCP subserver — answers_get returns detail; tools read-only."""

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.forms.answers import mcp as answers_mcp

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_answers_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/99",
        json={
            "id": 99,
            "created": "x",
            "survey": {"id": SID, "name": "F"},
            "data": [{"id": "q1", "label": "L", "type": "string", "value": "v"}],
        },
        status=200,
    )
    async with Client(answers_mcp.mcp) as client:
        result = await client.call_tool("answers_get", {"survey_id": SID, "answer_id": "99"})
    assert result.data.id == 99
    assert result.data.data[0].value == "v"


@responses.activate
async def test_answers_get_not_found_is_clean_error(creds):
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/answers/0", json={"errors": {}}, status=404)
    async with Client(answers_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("answers_get", {"survey_id": SID, "answer_id": "0"})


@responses.activate
async def test_answers_get_empty_response_guard(creds):
    """200 with empty body hits the id-is-None guard (blank object instead of 404)."""
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/answers/99", json={}, status=200)
    async with Client(answers_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("answers_get", {"survey_id": SID, "answer_id": "99"})


async def test_answers_tools_registered_read_only():
    async with Client(answers_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"answers_list", "answers_get"} <= set(tools)
    assert tools["answers_get"].annotations.readOnlyHint is True
