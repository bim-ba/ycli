"""TDD for forms answers MCP subserver — answers_get/answers_list reads + answers_export write."""

import json

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.answers import mcp as answers_mcp

pytestmark = pytest.mark.integration

SID = "6818ceffe010db4f59d11329"


@responses.activate
async def test_answers_get_tool_reads_flat_route(creds):
    """``answers_get`` hits the flat ``GET /v1/answers?answer_id=`` route (live-verified 200)."""
    responses.add(
        responses.GET,
        f"{BASE}/answers",
        json={
            "id": 2469549806,
            "created": "2026-07-12T10:00:00Z",
            "survey": {"id": SID, "name": "Feedback"},
            "data": [{"id": "1", "label": "Q1", "type": "string", "value": "x"}],
        },
        status=200,
    )
    async with Client(answers_mcp.mcp) as client:
        result = await client.call_tool("answers_get", {"answer_id": 2469549806})
    request = responses.calls[0].request
    assert request.method == "GET"
    assert request.url == f"{BASE}/answers?answer_id=2469549806"
    assert result.data.id == 2469549806
    assert result.data.survey.name == "Feedback"


@responses.activate
async def test_answers_get_tool_requires_exactly_one_selector(creds):
    async with Client(answers_mcp.mcp) as client:
        with pytest.raises(ToolError, match="exactly one"):
            await client.call_tool("answers_get", {})
        with pytest.raises(ToolError, match="exactly one"):
            await client.call_tool("answers_get", {"answer_id": 1, "answer_key": "k"})
    assert len(responses.calls) == 0  # rejected client-side — nothing was sent


@responses.activate
async def test_answers_export_tool_starts_async_export(creds):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/answers/export",
        json={"id": "op-4a1b", "status": "wait"},
        status=202,
    )
    async with Client(answers_mcp.mcp) as client:
        result = await client.call_tool(
            "answers_export", {"survey_id": SID, "body": {"format": "csv", "limit": 100}}
        )
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/answers/export"
    body = request.body
    assert isinstance(body, bytes)  # narrows Optional for json.loads
    assert json.loads(body) == {"format": "csv", "limit": 100}
    assert result.data.id == "op-4a1b" and result.data.status == "wait"


async def test_answers_tools_registered_with_honest_annotations():
    async with Client(answers_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"answers_get", "answers_list", "answers_export"}
    # answers_get wraps the flat GET /v1/answers?answer_id=|answer_key= route (live-verified).
    assert tools["answers_get"].annotations.readOnlyHint is True
    assert tools["answers_list"].annotations.readOnlyHint is True
    export = tools["answers_export"].annotations
    assert export.readOnlyHint is False
    assert export.destructiveHint is False and export.idempotentHint is False
    assert all(t.annotations.title for t in tools.values())
