"""Deterministic enumerators of ycli's public surface (CLI tree + MCP tool names)."""

from __future__ import annotations

import asyncio
from typing import Any

import typer
import typer.main
from fastmcp import Client

from ycli.cli.app import app
from ycli.mcp import mcp


def _walk(command, context: typer.Context, prefix: str) -> list[tuple[str, Any]]:
    """Every ``(path, command)`` under ``command``; list/get_command, as the root is lazy."""
    out: list[tuple[str, Any]] = []
    if not hasattr(command, "list_commands"):
        return out
    for name in sorted(command.list_commands(context)):
        sub = command.get_command(context, name)
        path = f"{prefix} {name}".strip()
        out.append((path, sub))
        out += _walk(sub, typer.Context(sub, parent=context, info_name=name), path)
    return out


def _commands() -> list[tuple[str, Any]]:
    root = typer.main.get_command(app)
    return _walk(root, typer.Context(root, info_name="ycli"), "")


def cli_tree() -> list[str]:
    """Every CLI command path (space-joined), sorted, e.g. 'tracker issues get'."""
    return [path for path, _ in _commands()]


def _cli_param(param: Any) -> str:
    """``--limit`` / ``KEY``, with ``!`` when required."""
    longest_opt = max(param.opts, key=len)
    label = str(longest_opt) if param.param_type_name == "option" else str(param.name).upper()
    return f"{label}!" if param.required else label


def cli_signatures() -> list[str]:
    """Each leaf command with its parameters, e.g. ``tracker issues get: KEY!``."""
    return [
        f"{path}: {' '.join(sorted(_cli_param(p) for p in command.params))}".rstrip(": ")
        for path, command in _commands()
        if not hasattr(command, "list_commands")
    ]


def _tools() -> list:
    async def go() -> list:
        async with Client(mcp) as client:
            return await client.list_tools()

    return asyncio.run(go())


def mcp_tool_names() -> list[str]:
    """Every MCP tool name, sorted (protocol-level, via the in-memory client)."""
    return sorted(tool.name for tool in _tools())


def mcp_signatures() -> list[str]:
    """Each MCP tool with its input parameters, e.g. ``tracker_issues_get(key!)``."""
    lines = []
    for tool in _tools():
        required = set(tool.inputSchema.get("required", []))
        params = sorted(tool.inputSchema.get("properties", {}))
        lines.append(f"{tool.name}({', '.join(p + '!' * (p in required) for p in params)})")
    return sorted(lines)
