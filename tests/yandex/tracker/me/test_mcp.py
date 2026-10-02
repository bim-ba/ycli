"""The Tracker auth probe's MCP guards the contract table cannot reach."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import TRACKER_BASE as BASE
from ycli.mcp.server import mcp


@pytest.mark.parametrize(
    ("status", "body", "match"),
    [
        (401, {}, "401"),
        # A 200 with no login (e.g. missing permissions) is a failed probe, not a blank user.
        (200, {}, "empty user"),
    ],
)
async def test_a_failed_probe_is_an_error(api, status, body, match):
    api.add("GET", f"{BASE}/myself", json=body, status=status)
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match=match):
            await client.call_tool("tracker_me_get", {})
