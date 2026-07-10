"""TDD for forms filling MCP subserver — only the read-only filling_get tool is exposed."""

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from ycli.yandex.forms.filling import mcp as filling_mcp

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_filling_get_tool_returns_fillable_form(creds):
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/form",
        json={"id": SID, "name": "Feedback", "pages": [{"items": []}]},
        status=200,
    )
    async with Client(filling_mcp.mcp) as client:
        result = await client.call_tool("filling_get", {"survey": SID})
    assert result.data.id == SID and result.data.name == "Feedback"


@responses.activate
async def test_filling_get_empty_response_guard(creds):
    """200 with empty body hits the id-is-None guard (blank object instead of 404)."""
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/form", json={}, status=200)
    async with Client(filling_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("filling_get", {"survey": SID})


async def test_filling_tools_registered_read_only():
    async with Client(filling_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"filling_get"}  # submit (write) and suggest (verb) stay off MCP
    assert tools["filling_get"].annotations.readOnlyHint is True
