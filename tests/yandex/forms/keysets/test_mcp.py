"""TDD for forms keysets MCP subserver — reads only (list/get).

The tools reach the key-set client through ``FormsClient.keysets``, so these pass once the
integrator wires ``self.keysets = KeysetsClient(session=transport)`` into ``forms/client.py``.
"""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.forms.keysets import mcp as keysets_mcp

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
KID = 7


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


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


async def test_keysets_tools_registered_read_only():
    async with Client(keysets_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"keysets_list", "keysets_get"}
    assert tools["keysets_list"].annotations.readOnlyHint is True
    assert tools["keysets_get"].annotations.readOnlyHint is True
