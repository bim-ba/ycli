"""TDD for forms keysets MCP subserver — reads + writes with honest annotations.

The tools reach the key-set client through ``FormsClient.keysets``, so these pass once the
integrator wires ``self.keysets = KeysetsClient(session=transport)`` into ``forms/client.py``.
"""

import json

import responses
from fastmcp import Client

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.keysets import mcp as keysets_mcp

SID = "6818ceffe010db4f59d11329"
KID = 7


@responses.activate
async def test_keysets_list_tool_returns_flat_collection(creds):
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets",
        json=[{"id": 7, "name": "Q1"}, {"id": 8, "name": "Q2"}],
        status=200,
    )
    async with Client(keysets_mcp.mcp) as client:
        result = await client.call_tool("keysets_list", {"survey_id": SID})
    assert [k.id for k in result.data] == [7, 8]


@responses.activate
async def test_keysets_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/keysets/{KID}",
        json={"id": KID, "name": "Q1", "used": 3},
        status=200,
    )
    async with Client(keysets_mcp.mcp) as client:
        result = await client.call_tool("keysets_get", {"survey_id": SID, "keyset_id": KID})
    assert result.data.id == KID and result.data.used == 3


@responses.activate
async def test_keysets_create_tool_posts_body(creds):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/keysets",
        json={"id": KID, "name": "Q1", "total": 250, "is_enabled": True},
        status=201,
    )
    async with Client(keysets_mcp.mcp) as client:
        result = await client.call_tool(
            "keysets_create",
            {"survey_id": SID, "body": {"name": "Q1", "total": 250, "is_enabled": True}},
        )
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/keysets"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"name": "Q1", "total": 250, "is_enabled": True}
    assert result.data.id == KID and result.data.is_enabled is True


@responses.activate
async def test_keysets_modify_tool_patches_full_record(creds):
    responses.add(
        responses.PATCH,
        f"{BASE}/surveys/{SID}/keysets/{KID}",
        json={"id": KID, "name": "Q1", "total": 250, "is_enabled": False},
        status=200,
    )
    async with Client(keysets_mcp.mcp) as client:
        result = await client.call_tool(
            "keysets_modify",
            {
                "survey_id": SID,
                "keyset_id": KID,
                "body": {"name": "Q1", "total": 250, "is_enabled": False},
            },
        )
    request = responses.calls[0].request
    assert request.method == "PATCH" and request.url == f"{BASE}/surveys/{SID}/keysets/{KID}"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"name": "Q1", "total": 250, "is_enabled": False}
    assert result.data.is_enabled is False


@responses.activate
async def test_keysets_delete_tool_returns_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/keysets/{KID}", status=200)
    async with Client(keysets_mcp.mcp) as client:
        result = await client.call_tool("keysets_delete", {"survey_id": SID, "keyset_id": KID})
    request = responses.calls[0].request
    assert request.method == "DELETE" and request.url == f"{BASE}/surveys/{SID}/keysets/{KID}"
    assert result.data.ok is True and str(KID) in result.data.detail


async def test_keysets_tools_registered_with_honest_annotations():
    async with Client(keysets_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "keysets_list",
        "keysets_get",
        "keysets_create",
        "keysets_modify",
        "keysets_delete",
    }
    assert tools["keysets_list"].annotations.readOnlyHint is True
    assert tools["keysets_get"].annotations.readOnlyHint is True
    create = tools["keysets_create"].annotations
    assert create.readOnlyHint is False
    assert create.destructiveHint is False and create.idempotentHint is False
    modify = tools["keysets_modify"].annotations
    assert modify.readOnlyHint is False
    assert modify.destructiveHint is False and modify.idempotentHint is True
    delete = tools["keysets_delete"].annotations
    assert delete.readOnlyHint is False
    assert delete.destructiveHint is True and delete.idempotentHint is False
    assert all(t.annotations.title for t in tools.values())
