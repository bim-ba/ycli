"""Tracker local-fields MCP guards the contract table cannot reach."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import TRACKER_BASE as BASE
from ycli.mcp.server import mcp


async def test_an_empty_local_field_is_an_error(api):
    api.add("GET", f"{BASE}/queues/ORG/localFields/ghost", json={})
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="not found"):
            await client.call_tool(
                "tracker_localfields_get", {"queue_id": "ORG", "field_key": "ghost"}
            )
