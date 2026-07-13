"""TDD for forms questions MCP subserver — reads + writes with honest annotations."""

import json
from urllib.parse import parse_qs, urlparse

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.questions import mcp as questions_mcp

pytestmark = pytest.mark.integration

SID = "6818ceffe010db4f59d11329"


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


@responses.activate
async def test_questions_create_tool_posts_typed_body(creds):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 17, "type": "string", "label": "Name"},
        status=201,
    )
    async with Client(questions_mcp.mcp) as client:
        result = await client.call_tool(
            "questions_create", {"survey_id": SID, "body": {"type": "string", "label": "Name"}}
        )
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/questions"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"type": "string", "label": "Name"}
    assert result.data.id == 17 and result.data.label == "Name"


@responses.activate
async def test_questions_modify_tool_patches_typed_body(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/surveys/{SID}/questions/17",
        json={"id": 17, "type": "string", "label": "Full name"},
        status=200,
    )
    async with Client(questions_mcp.mcp) as client:
        result = await client.call_tool(
            "questions_modify",
            {
                "survey_id": SID,
                "question_id": "17",
                "body": {"type": "string", "label": "Full name"},
            },
        )
    request = responses.calls[0].request
    assert request.method == "PATCH" and request.url == f"{BASE}/surveys/{SID}/questions/17"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"type": "string", "label": "Full name"}
    assert result.data.label == "Full name"


@responses.activate
async def test_questions_delete_tool_forwards_force(creds):
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/questions/17", status=204)
    async with Client(questions_mcp.mcp) as client:
        result = await client.call_tool(
            "questions_delete", {"survey_id": SID, "question_id": "17", "force": True}
        )
    request = responses.calls[0].request
    assert request.method == "DELETE"
    url = request.url
    assert url is not None
    parsed = urlparse(url)
    assert parsed.path.endswith(f"/surveys/{SID}/questions/17")
    assert parse_qs(parsed.query) == {"force": ["true"]}
    assert result.data.ok is True and result.data.detail == f"deleted question 17 on survey {SID}"


@responses.activate
async def test_questions_move_tool_posts_target(creds):
    responses.add(
        responses.POST, f"{BASE}/surveys/{SID}/questions/17/move", json={"id": 17}, status=200
    )
    async with Client(questions_mcp.mcp) as client:
        result = await client.call_tool(
            "questions_move",
            {"survey_id": SID, "question_id": "17", "body": {"page": 2, "position": 1}},
        )
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/questions/17/move"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"page": 2, "position": 1}
    assert result.data.id == 17


async def test_questions_move_tool_rejects_bare_position(creds):
    """A bare ``position`` with no target used to silently re-page to 1; MCP callers now get a
    clear validation error instead (owner-approved behavior change; the CLI still defaults
    ``page=1`` visibly before constructing the body — see ``cli.move``)."""
    async with Client(questions_mcp.mcp) as client:
        with pytest.raises(ToolError, match="question move needs a target"):
            await client.call_tool(
                "questions_move", {"survey_id": SID, "question_id": "17", "body": {"position": 1}}
            )


async def test_questions_tools_registered_with_honest_annotations():
    async with Client(questions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "questions_list",
        "questions_get",
        "questions_create",
        "questions_modify",
        "questions_delete",
        "questions_move",
    }
    for name in ("questions_list", "questions_get"):
        assert tools[name].annotations.readOnlyHint is True
    for name in ("questions_create", "questions_move"):
        ann = tools[name].annotations
        assert ann.readOnlyHint is False
        assert ann.destructiveHint is False and ann.idempotentHint is False
    modify = tools["questions_modify"].annotations
    assert modify.readOnlyHint is False
    assert modify.destructiveHint is False and modify.idempotentHint is True
    delete = tools["questions_delete"].annotations
    assert delete.readOnlyHint is False
    assert delete.destructiveHint is True and delete.idempotentHint is False
    assert all(t.annotations.title for t in tools.values())
