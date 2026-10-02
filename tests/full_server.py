"""The unfiltered root MCP server, built once for the tests that exercise every tool."""

from fastmcp.tools import Tool

from ycli.mcp.selection import Selection
from ycli.mcp.server import build_server

mcp = build_server(Selection())


async def tool_with_output_schema(name: str) -> Tool:
    """One tool as the server holds it: ``tools/list`` drops the output schemas."""
    tool = await mcp.get_tool(name)
    assert tool is not None, name
    return tool


async def tools_with_output_schemas() -> list[Tool]:
    """Every served tool as the server holds it."""
    return [await tool_with_output_schema(tool.name) for tool in await mcp.list_tools()]
