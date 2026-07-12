"""TDD for the tracker issuetypes MCP subserver — reads + writes with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.issuetypes import mcp as issuetypes_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_issuetypes_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/issuetypes/", json={"id": 5, "key": "bug2"}, status=201)
    async with Client(issuetypes_mcp.mcp) as client:
        result = await client.call_tool(
            "issuetypes_create", {"body": {"key": "bug2", "name": {"ru": "Ошибка", "en": "Bug2"}}}
        )
    assert result.data.key == "bug2"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issuetypes/"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "key": "bug2",
        "name": {"ru": "Ошибка", "en": "Bug2"},
    }


@responses.activate
async def test_issuetypes_edit_tool_sends_version(creds):
    responses.add(
        responses.PATCH, f"{BASE}/issuetypes/5", json={"id": 5, "key": "bug2"}, status=200
    )
    async with Client(issuetypes_mcp.mcp) as client:
        result = await client.call_tool(
            "issuetypes_edit",
            {"issue_type_id": "5", "body": {"name": {"ru": "Дефект"}}, "version": 2},
        )
    assert result.data.key == "bug2"
    assert responses.calls[0].request.method == "PATCH"
    assert "version=2" in (responses.calls[0].request.url or "")
    assert json.loads(responses.calls[0].request.body) == {"name": {"ru": "Дефект"}}  # ty: ignore[invalid-argument-type]


async def test_issuetype_tools_annotations():
    async with Client(issuetypes_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["issuetypes_list"].annotations.readOnlyHint is True
    expected = {  # tool -> (destructiveHint, idempotentHint)
        "issuetypes_create": (False, False),
        "issuetypes_edit": (False, True),
    }
    for name, (destructive, idempotent) in expected.items():
        ann = tools[name].annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is destructive, name
        assert ann.idempotentHint is idempotent, name
        assert ann.title, name
