"""Forms files FastMCP subserver — intentionally tool-less.

ARCH-1 gives every resource package the four surface files, but this resource exposes **no** MCP
tools: ``upload`` / ``download`` are binary or write, ``delete`` is a write, and ``verify`` is a
read done via POST whose verb is not an MCP read verb. So the subserver is created for symmetry
and mounts cleanly, but registers nothing — reach these endpoints via the CLI or SDK.
"""

from fastmcp import FastMCP

mcp = FastMCP("forms-files")
