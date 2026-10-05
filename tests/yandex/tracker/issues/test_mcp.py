"""`tracker_issues_get` on a reply that is not an issue."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.full_server import mcp
from tests.hosts import TRACKER_BASE as BASE


async def test_a_reply_that_does_not_fit_its_model_is_a_tool_error_naming_the_call(api):
    api.add("GET", f"{BASE}/issues/DE-1", json=["not", "an", "issue"])
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match=r"the reply to GET issues/DE-1 does not fit"):
            await client.call_tool("tracker_issues_get", {"key": "DE-1"})
    assert len(api.calls) == 1
