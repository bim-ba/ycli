"""`tracker_issues_get` refuses an empty answer instead of returning a blank issue."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.full_server import mcp
from tests.hosts import TRACKER_BASE as BASE


async def test_an_empty_answer_is_an_error(api):
    api.add("GET", f"{BASE}/issues/DE-1", json={})
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="empty response"):
            await client.call_tool("tracker_issues_get", {"key": "DE-1"})
