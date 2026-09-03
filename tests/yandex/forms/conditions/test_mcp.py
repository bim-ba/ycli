"""TDD for forms conditions MCP subserver — 18 tools, honest annotations, guarded gets."""

import json

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.conditions import mcp as conditions_mcp

pytestmark = pytest.mark.integration

SID = "6818ceffe010db4f59d11329"
QID = "17"
PID = 3
CID = 5
GROUP = {
    "id": CID,
    "operator": "and",
    "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
}
ENVELOPE = {"operator": "and", "items": [GROUP]}
WIRE_BODY = {
    "operator": "and",
    "items": [{"type": "question", "condition": "eq", "question": "q1", "value": "yes"}],
}

FAMILIES = [
    (
        "question",
        f"surveys/{SID}/questions/{QID}/conditions",
        {"survey_id": SID, "question_id": QID},
    ),
    ("page", f"surveys/{SID}/pages/{PID}/conditions", {"survey_id": SID, "page_id": PID}),
    ("submit", f"surveys/{SID}/conditions", {"survey_id": SID}),
]
DELETE_DETAIL = {
    "question": f"deleted condition {CID} from question {QID}",
    "page": f"deleted condition {CID} from page {PID}",
    "submit": f"deleted condition {CID} from survey {SID}",
}


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
async def test_list_tool_returns_envelope(family, path, ancestors, creds):
    responses.add(responses.GET, f"{BASE}/{path}", json=ENVELOPE, status=200)
    async with Client(conditions_mcp.mcp) as client:
        result = await client.call_tool(f"conditions_{family}_list", ancestors)
    assert result.data.operator == "and" and result.data.items[0].id == CID


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
async def test_get_tool_returns_group(family, path, ancestors, creds):
    responses.add(responses.GET, f"{BASE}/{path}/{CID}", json=GROUP, status=200)
    async with Client(conditions_mcp.mcp) as client:
        result = await client.call_tool(
            f"conditions_{family}_get", {**ancestors, "condition_id": CID}
        )
    assert result.data.id == CID and result.data.operator == "and"


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
async def test_create_tool_posts_typed_body(family, path, ancestors, creds):
    responses.add(responses.POST, f"{BASE}/{path}", json=GROUP, status=200)
    async with Client(conditions_mcp.mcp) as client:
        result = await client.call_tool(
            f"conditions_{family}_create", {**ancestors, "body": WIRE_BODY}
        )
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/{path}"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == WIRE_BODY
    assert result.data.id == CID


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
async def test_modify_tool_patches_full_group(family, path, ancestors, creds):
    responses.add(responses.PATCH, f"{BASE}/{path}/{CID}", json=GROUP, status=200)
    async with Client(conditions_mcp.mcp) as client:
        result = await client.call_tool(
            f"conditions_{family}_modify", {**ancestors, "condition_id": CID, "body": WIRE_BODY}
        )
    request = responses.calls[0].request
    assert request.method == "PATCH" and request.url == f"{BASE}/{path}/{CID}"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == WIRE_BODY
    assert result.data.id == CID


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
async def test_delete_tool_returns_ack(family, path, ancestors, creds):
    responses.add(responses.DELETE, f"{BASE}/{path}/{CID}", status=200)
    async with Client(conditions_mcp.mcp) as client:
        result = await client.call_tool(
            f"conditions_{family}_delete", {**ancestors, "condition_id": CID}
        )
    request = responses.calls[0].request
    assert request.method == "DELETE" and request.url == f"{BASE}/{path}/{CID}"
    assert result.data.ok is True and result.data.detail == DELETE_DETAIL[family]


@pytest.mark.parametrize(("family", "path", "ancestors"), FAMILIES)
@responses.activate
async def test_set_operator_tool_patches_collection(family, path, ancestors, creds):
    responses.add(responses.PATCH, f"{BASE}/{path}", json=ENVELOPE, status=200)
    async with Client(conditions_mcp.mcp) as client:
        result = await client.call_tool(
            f"conditions_{family}_set_operator", {**ancestors, "operator": "or"}
        )
    request = responses.calls[0].request
    assert request.method == "PATCH" and request.url == f"{BASE}/{path}"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"operator": "or"}
    assert result.data.items[0].id == CID


@responses.activate
async def test_conditions_question_get_empty_response_guard(creds):
    responses.add(
        responses.GET, f"{BASE}/surveys/{SID}/questions/{QID}/conditions/{CID}", json={}, status=200
    )
    async with Client(conditions_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "conditions_question_get",
                {"survey_id": SID, "question_id": QID, "condition_id": CID},
            )


async def test_conditions_tools_registered_with_honest_annotations():
    async with Client(conditions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "conditions_question_list",
        "conditions_question_get",
        "conditions_question_create",
        "conditions_question_modify",
        "conditions_question_delete",
        "conditions_question_set_operator",
        "conditions_page_list",
        "conditions_page_get",
        "conditions_page_create",
        "conditions_page_modify",
        "conditions_page_delete",
        "conditions_page_set_operator",
        "conditions_submit_list",
        "conditions_submit_get",
        "conditions_submit_create",
        "conditions_submit_modify",
        "conditions_submit_delete",
        "conditions_submit_set_operator",
    }
    for family in ("question", "page", "submit"):
        assert tools[f"conditions_{family}_list"].annotations.readOnlyHint is True
        assert tools[f"conditions_{family}_get"].annotations.readOnlyHint is True
        create = tools[f"conditions_{family}_create"].annotations
        assert create.readOnlyHint is False
        assert create.destructiveHint is False and create.idempotentHint is False
        modify = tools[f"conditions_{family}_modify"].annotations
        assert modify.readOnlyHint is False
        assert modify.destructiveHint is False and modify.idempotentHint is True
        set_operator = tools[f"conditions_{family}_set_operator"].annotations
        assert set_operator.readOnlyHint is False
        assert set_operator.destructiveHint is False and set_operator.idempotentHint is True
        delete = tools[f"conditions_{family}_delete"].annotations
        assert delete.readOnlyHint is False
        assert delete.destructiveHint is True and delete.idempotentHint is False
    assert all(t.annotations.title for t in tools.values())
