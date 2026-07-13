"""TDD for forms surveys MCP subserver — reads + writes with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.surveys import mcp as surveys_mcp

pytestmark = pytest.mark.integration

SID = "6818ceffe010db4f59d11329"


@responses.activate
async def test_surveys_list_tool_returns_flat_collection(creds):
    responses.add(
        responses.GET,
        f"{BASE}/surveys",
        json={"links": {}, "result": [{"id": "a"}, {"id": "b"}]},
        status=200,
    )
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


@responses.activate
async def test_surveys_create_tool_posts_body(creds):
    responses.add(
        responses.POST, f"{BASE}/surveys", json={"id": SID, "name": "Onboarding"}, status=201
    )
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_create", {"body": {"name": "Onboarding"}})
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"name": "Onboarding"}  # unset fields are dropped
    assert result.data.id == SID and result.data.name == "Onboarding"


@responses.activate
async def test_surveys_modify_tool_patches_body(creds):
    responses.add(
        responses.PATCH, f"{BASE}/surveys/{SID}", json={"id": SID, "name": "Renamed"}, status=200
    )
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool(
            "surveys_modify", {"survey_id": SID, "body": {"name": "Renamed"}}
        )
    request = responses.calls[0].request
    assert request.method == "PATCH" and request.url == f"{BASE}/surveys/{SID}"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"name": "Renamed"}
    assert result.data.name == "Renamed"


@responses.activate
async def test_surveys_delete_tool(creds):
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}", status=204)
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_delete", {"survey_id": SID})
    request = responses.calls[0].request
    assert request.method == "DELETE" and request.url == f"{BASE}/surveys/{SID}"
    assert result.data.ok is True and result.data.detail == f"deleted survey {SID}"


@responses.activate
async def test_surveys_publish_tool(creds):
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/publish", status=200)
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_publish", {"survey_id": SID})
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/publish"
    assert result.data.ok is True and result.data.detail == f"published survey {SID}"


@responses.activate
async def test_surveys_unpublish_tool(creds):
    responses.add(responses.POST, f"{BASE}/surveys/{SID}/unpublish", status=200)
    async with Client(surveys_mcp.mcp) as client:
        result = await client.call_tool("surveys_unpublish", {"survey_id": SID})
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/unpublish"
    assert result.data.ok is True and result.data.detail == f"unpublished survey {SID}"


async def test_surveys_tools_registered_with_honest_annotations():
    async with Client(surveys_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "surveys_list",
        "surveys_get",
        "surveys_create",
        "surveys_modify",
        "surveys_delete",
        "surveys_publish",
        "surveys_unpublish",
    }
    for name in ("surveys_list", "surveys_get"):
        assert tools[name].annotations.readOnlyHint is True
    for name in ("surveys_create", "surveys_publish", "surveys_unpublish"):
        ann = tools[name].annotations
        assert ann.readOnlyHint is False
        assert ann.destructiveHint is False and ann.idempotentHint is False
    modify = tools["surveys_modify"].annotations
    assert modify.readOnlyHint is False
    assert modify.destructiveHint is False and modify.idempotentHint is True
    delete = tools["surveys_delete"].annotations
    assert delete.readOnlyHint is False
    assert delete.destructiveHint is True and delete.idempotentHint is False
    assert all(t.annotations.title for t in tools.values())
