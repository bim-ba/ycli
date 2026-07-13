"""Every MCP tool carries the read/idempotent/open-world hints + a title; servers have instructions."""  # noqa: E501

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
        assert isinstance(ann.readOnlyHint, bool), f"{tool.name} must declare readOnlyHint"
        assert ann.openWorldHint is True, tool.name
        if ann.readOnlyHint:
            assert ann.idempotentHint is True, tool.name
        else:
            # Writes declare their remaining hints explicitly — the MCP-spec default
            # for an unannotated tool is destructiveHint=true (see ARCH-3).
            assert isinstance(ann.destructiveHint, bool), (
                f"{tool.name} write tool must declare destructiveHint"
            )
            assert isinstance(ann.idempotentHint, bool), (
                f"{tool.name} write tool must declare idempotentHint"
            )
        assert ann.title and ann.title.strip(), f"{tool.name} has no title"


def test_servers_have_instructions():
    for server in (root_mcp, tracker_mcp, wiki_mcp, forms_mcp):
        assert server.instructions and server.instructions.strip()
