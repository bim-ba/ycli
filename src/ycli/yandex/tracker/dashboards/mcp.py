"""Tracker dashboards FastMCP subserver — intentionally tool-less.

Creating a dashboard and adding a widget are WRITES, and the MCP surface is read-only
(ARCH-3), so this resource registers NO tools. The empty ``FastMCP`` instance exists only to
satisfy the four-surface symmetry invariant (ARCH-1). Dashboard writes live on the SDK + CLI
(``tracker dashboards …``).
"""

from fastmcp import FastMCP

mcp = FastMCP("tracker-dashboards")
