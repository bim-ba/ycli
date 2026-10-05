"""The Tracker auth probe over MCP, where a contract case cannot reach."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.full_server import mcp
from tests.hosts import TRACKER_BASE as BASE


async def test_a_rejected_token_fails_the_probe(api):
    api.add("GET", f"{BASE}/myself", json={}, status=401)
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="401"):
            await client.call_tool("tracker_me_get", {})
