"""TDD for forms filling MCP subserver — get/suggest reads + the submit write."""

import json
from urllib.parse import parse_qs, urlparse

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.filling import mcp as filling_mcp

SID = "6818ceffe010db4f59d11329"


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


@responses.activate
async def test_filling_suggest_tool_forwards_query(creds):
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/suggest",
        json=[{"layer": "city", "id": "1", "text": "Berlin"}],
        status=200,
    )
    async with Client(filling_mcp.mcp) as client:
        result = await client.call_tool(
            "filling_suggest", {"survey": SID, "question": "city_1", "text": "Ber"}
        )
    request = responses.calls[0].request
    url = request.url
    assert url is not None
    parsed = urlparse(url)
    assert request.method == "GET" and parsed.path.endswith(f"/surveys/{SID}/suggest")
    assert parse_qs(parsed.query) == {"question": ["city_1"], "text": ["Ber"]}
    assert [s.text for s in result.data] == ["Berlin"]


@responses.activate
async def test_filling_submit_tool_posts_answer_map(creds):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/form",
        json={"id": SID, "answer_id": 99},
        status=200,
    )
    async with Client(filling_mcp.mcp) as client:
        result = await client.call_tool(
            "filling_submit", {"survey": SID, "body": {"answer_short_text_1": "Ann"}}
        )
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/form"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"answer_short_text_1": "Ann"}
    assert result.data.answer_id == 99


@responses.activate
async def test_filling_submit_tool_dry_run_query(creds):
    responses.add(
        responses.POST, f"{BASE}/surveys/{SID}/form", json={"id": SID, "title": "ok"}, status=200
    )
    async with Client(filling_mcp.mcp) as client:
        await client.call_tool(
            "filling_submit",
            {"survey": SID, "body": {"answer_short_text_1": "Ann"}, "dry_run": True, "key": "k1"},
        )
    url = responses.calls[0].request.url
    assert url is not None
    parsed = urlparse(url)
    assert parse_qs(parsed.query) == {"dry_run": ["true"], "key": ["k1"]}


async def test_filling_tools_registered_with_honest_annotations():
    async with Client(filling_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"filling_get", "filling_suggest", "filling_submit"}
    assert tools["filling_get"].annotations.readOnlyHint is True
    assert tools["filling_suggest"].annotations.readOnlyHint is True
    submit = tools["filling_submit"].annotations
    assert submit.readOnlyHint is False
    assert submit.destructiveHint is False and submit.idempotentHint is False
    assert all(t.annotations.title for t in tools.values())
