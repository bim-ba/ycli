"""TDD for forms questions MCP subserver — questions_get returns a Question; read-only."""

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.forms.questions import mcp as questions_mcp

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_questions_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/questions/17",
        json={"id": 17, "slug": "s1", "type": "string", "label": "Name"},
        status=200,
    )
    async with Client(questions_mcp.mcp) as client:
        result = await client.call_tool("questions_get", {"survey_id": SID, "question_id": "17"})
    assert result.data.id == 17 and result.data.slug == "s1"


@responses.activate
async def test_questions_get_not_found_is_clean_error(creds):
    responses.add(
        responses.GET, f"{BASE}/surveys/{SID}/questions/0", json={"errors": {}}, status=404
    )
    async with Client(questions_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("questions_get", {"survey_id": SID, "question_id": "0"})


@responses.activate
async def test_questions_get_empty_response_guard(creds):
    """200 with empty body hits the id-is-None guard (blank object instead of 404)."""
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/questions/17", json={}, status=200)
    async with Client(questions_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("questions_get", {"survey_id": SID, "question_id": "17"})


async def test_questions_tools_registered_read_only():
    async with Client(questions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {"questions_list", "questions_get"} <= set(tools)
    assert tools["questions_get"].annotations.readOnlyHint is True
