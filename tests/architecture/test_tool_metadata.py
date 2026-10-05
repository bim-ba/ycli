"""Every MCP tool has a description and an output schema."""

from __future__ import annotations

import asyncio

from tests.architecture.scanners import _probe_tools
from tests.full_server import tools_with_output_schemas


def test_every_mcp_tool_has_description_and_output_schema():
    """Every tool has a docstring-derived description and a return-annotation-derived output schema.

    The docstring IS the client-facing description (the LLM's selector).
    The return type annotation IS the output schema (auto-derived by fastmcp).
    Both are required — omitting either makes the tool invisible or unusable to agents.
    See docs/conventions/resources.md §MCP tool-metadata standard.
    """
    tools = asyncio.run(tools_with_output_schemas())  # the listing itself carries none
    assert tools, "no MCP tools discovered"
    assert _undescribed_tools(tools) == []


def _undescribed_tools(tools) -> list[str]:
    """Tools with no docstring (→ description) or no return annotation (→ output schema)."""
    return [tool.name for tool in tools if not tool.description or tool.output_schema is None]


def test_the_description_and_output_schema_check_bites():
    def register(server):
        @server.tool
        def no_docstring() -> str:
            return ""

        @server.tool
        def no_return_type():
            """Probe."""

        @server.tool
        def complete() -> str:
            """Probe."""
            return ""

    assert sorted(_undescribed_tools(_probe_tools(register))) == ["no_docstring", "no_return_type"]
