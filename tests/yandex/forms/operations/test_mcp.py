"""TDD for forms operations MCP subserver — operations_get returns status; tool read-only."""

import pytest
import responses
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.operations import mcp as operations_mcp

OID = "op-4a1b"


@responses.activate
async def test_operations_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/operations/{OID}",
        json={"id": OID, "status": "ok", "message": "done"},
        status=200,
    )
    async with Client(operations_mcp.mcp) as client:
        result = await client.call_tool("operations_get", {"operation_id": OID})
    assert result.data.id == OID and result.data.status == "ok"


@responses.activate
async def test_operations_get_empty_response_is_clean_error(creds):
    """A 200 with an empty body hits the id-is-None guard (a clean error, not a phantom object)."""
    responses.add(responses.GET, f"{BASE}/operations/{OID}", json={}, status=200)
    async with Client(operations_mcp.mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("operations_get", {"operation_id": OID})


async def test_operations_tool_registered_read_only():
    async with Client(operations_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "operations_get" in tools
    assert tools["operations_get"].annotations.readOnlyHint is True
