"""Wiki MCP behaviour a contract case cannot express: guards and what is never exposed."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.hosts import WIKI_BASE as BASE
from ycli.mcp.server import mcp


async def test_an_empty_user_fails_the_auth_probe(api):
    api.add("GET", f"{BASE}/users/me", json={})
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="auth probe failed"):
            await client.call_tool("wiki_me_get", {})


async def test_no_tool_returns_attachment_bytes():
    """Binary downloads are CLI/SDK only; uploads take base64 in, nothing binary comes out."""
    async with Client(mcp) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert not any(name.startswith("wiki_") and "download" in name for name in names)
    assert {name for name in names if name.startswith("wiki_attachments_")} == {
        "wiki_attachments_list",
        "wiki_attachments_attach",
        "wiki_attachments_upload",
        "wiki_attachments_delete",
    }
