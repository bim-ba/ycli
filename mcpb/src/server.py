"""MCPB entry point: run the ycli MCP server over stdio."""

from ycli.mcp.server import main

main(read_only=False)
