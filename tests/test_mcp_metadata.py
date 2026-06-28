"""Every MCP tool carries the read/idempotent/open-world hints + a title; servers have instructions."""

from __future__ import annotations

import asyncio

from fastmcp import Client

from ycli.mcp import mcp as root_mcp
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp


def _tools():
    async def go():
        async with Client(root_mcp) as client:
            return await client.list_tools()

    return asyncio.run(go())


def test_every_tool_has_hints_and_title():
    tools = _tools()
    assert tools
    for tool in tools:
        ann = tool.annotations
        assert ann is not None, tool.name
        assert ann.readOnlyHint is True, tool.name
        assert ann.idempotentHint is True, tool.name
        assert ann.openWorldHint is True, tool.name
        assert ann.title and ann.title.strip(), f"{tool.name} has no title"


def test_servers_have_instructions():
    for server in (root_mcp, tracker_mcp, wiki_mcp, forms_mcp):
        assert server.instructions and server.instructions.strip()
