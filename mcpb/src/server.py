"""MCPB entry point: ``python -m ycli.mcp``, the MCP server over stdio.

It names no ycli function, so a change to the server's own entry cannot break the bundle.
"""

import runpy

runpy.run_module("ycli.mcp", run_name="__main__", alter_sys=True)
