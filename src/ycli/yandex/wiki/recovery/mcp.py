"""Wiki /recovery_tokens FastMCP subserver — intentionally tool-less.

Restoring a page is a WRITE (``POST /recovery_tokens/{token}/recover``), and the MCP surface
is read-only (ARCH-3), so this resource registers NO tools. The empty ``FastMCP`` instance
exists only to satisfy the four-surface symmetry invariant (ARCH-1): every resource package
ships the five canonical files. Restore lives on the SDK + CLI (``wiki recovery restore``).
"""

from fastmcp import FastMCP

mcp = FastMCP("wiki-recovery")
