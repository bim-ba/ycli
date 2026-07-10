"""Tracker data-import FastMCP subserver — intentionally tool-less.

Every import endpoint is a WRITE (admin-only), and the MCP surface is read-only (ARCH-3), so
this resource registers NO tools. The empty ``FastMCP`` instance exists only to satisfy the
four-surface symmetry invariant (ARCH-1). Imports live on the SDK + CLI (``tracker import …``).
"""

from fastmcp import FastMCP

mcp = FastMCP("tracker-import")
