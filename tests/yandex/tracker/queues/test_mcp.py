"""Tracker queues MCP guards the contract table cannot reach."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.full_server import mcp
from tests.hosts import TRACKER_BASE as BASE


async def test_an_empty_queue_is_an_error(api):
    # A 200 with an empty object means a wrong key or no access, not a blank queue.
    api.add("GET", f"{BASE}/queues/NOPE", json={})
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="not found"):
            await client.call_tool("tracker_queues_get", {"queue_id": "NOPE"})
