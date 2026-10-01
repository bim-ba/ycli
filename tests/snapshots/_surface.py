"""Deterministic enumerators of ycli's public surface (CLI tree + MCP tool names)."""

from __future__ import annotations

import asyncio

import typer
import typer.main
from fastmcp import Client

from ycli.cli.app import app
from ycli.mcp import mcp


def cli_tree() -> list[str]:
    """Every CLI command path (space-joined), sorted, e.g. 'tracker issues get'."""
    root = typer.main.get_command(app)

    # list_commands/get_command, not `.commands`: the root loads its sub-apps lazily.
    def walk(command, context: typer.Context, prefix: str) -> list[str]:
        out: list[str] = []
        if not hasattr(command, "list_commands"):
            return out
        for name in sorted(command.list_commands(context)):
            sub = command.get_command(context, name)
            path = f"{prefix} {name}".strip()
            out.append(path)
            out += walk(sub, typer.Context(sub, parent=context, info_name=name), path)
        return out

    return walk(root, typer.Context(root, info_name="ycli"), "")


def mcp_tool_names() -> list[str]:
    """Every MCP tool name, sorted (protocol-level, via the in-memory client)."""

    async def go() -> list[str]:
        async with Client(mcp) as client:
            return sorted(t.name for t in await client.list_tools())

    return asyncio.run(go())
