"""Deterministic enumerators of ycli's public surface (CLI tree + MCP tool names)."""
from __future__ import annotations

import asyncio

import typer.main
from fastmcp import Client

from ycli.cli import app
from ycli.mcp import mcp


def cli_tree() -> list[str]:
    """Every CLI command path (space-joined), sorted, e.g. 'tracker issues get'."""
    root = typer.main.get_command(app)

    def walk(command, prefix: str) -> list[str]:
        out: list[str] = []
        for name in sorted(getattr(command, "commands", {})):
            path = f"{prefix} {name}".strip()
            out.append(path)
            out += walk(command.commands[name], path)
        return out

    return walk(root, "")


def mcp_tool_names() -> list[str]:
    """Every MCP tool name, sorted (protocol-level, via the in-memory client)."""
    async def go() -> list[str]:
        async with Client(mcp) as client:
            return sorted(t.name for t in await client.list_tools())

    return asyncio.run(go())
