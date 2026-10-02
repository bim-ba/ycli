"""Deterministic enumerators of ycli's public surface (CLI tree and signatures, MCP signatures)."""

from __future__ import annotations

import asyncio
from typing import Any

import typer
import typer.main
from fastmcp import Client

from tests.full_server import mcp
from ycli.cli.app import app
from ycli.cli.lazy import LazyGroup


def _walk(
    command, context: typer.Context, prefix: str, *, hidden: bool = False
) -> list[tuple[str, Any]]:
    """Every ``(path, command)`` under ``command``; list/get_command, as the root is lazy.

    A hidden command is a deprecated alias of a visible one (``ycli.cli.aliases``): it is not
    part of the surface the snapshots and the contract table cover, unless ``hidden`` asks.
    """
    out: list[tuple[str, Any]] = []
    if not hasattr(command, "list_commands"):
        return out
    for name in sorted(command.list_commands(context)):
        sub = command.get_command(context, name)
        if isinstance(sub, LazyGroup):  # the stand-in lists a sub-app; walk the real one
            sub = sub.load()
        if sub.hidden and not hidden:
            continue
        path = f"{prefix} {name}".strip()
        out.append((path, sub))
        out += _walk(sub, typer.Context(sub, parent=context, info_name=name), path, hidden=hidden)
    return out


def _commands(*, hidden: bool = False) -> list[tuple[str, Any]]:
    root = typer.main.get_command(app)
    return _walk(root, typer.Context(root, info_name="ycli"), "", hidden=hidden)


def cli_tree() -> list[str]:
    """Every CLI command path (space-joined), sorted, e.g. 'tracker issues get'."""
    return [path for path, _ in _commands()]


def _cli_param(param: Any) -> str:
    """``--limit:INTEGER=0`` / ``KEY:TEXT!`` — name, type, then ``!`` (required) or the default."""
    longest_opt = max(param.opts, key=len)
    label = str(longest_opt) if param.param_type_name == "option" else str(param.name).upper()
    label = f"{label}:{param.type.name.upper()}"
    if param.required:
        return f"{label}!"
    return label if param.default is None else f"{label}={param.default!r}"


def cli_leaves() -> dict[str, Any]:
    """Every visible leaf command by space-joined path, e.g. ``'tracker issues get'``."""
    return {path: command for path, command in _commands() if not hasattr(command, "list_commands")}


def cli_hidden_leaves() -> dict[str, Any]:
    """Every hidden leaf command, or leaf under a hidden group, by space-joined path."""
    visible = set(cli_leaves())
    return {
        path: command
        for path, command in _commands(hidden=True)
        if not hasattr(command, "list_commands") and path not in visible
    }


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


def mcp_signatures() -> list[str]:
    """Each MCP tool with typed parameters, e.g. ``tracker_issues_get(key:string!)``."""

    def describe(name: str, schema: dict, required: bool) -> str:
        kind = (
            schema.get("type")
            or "|".join(
                str(option.get("type", option.get("$ref", "?")).rsplit("/", 1)[-1])
                for option in schema.get("anyOf", [])
            )
            or str(schema.get("$ref", "?")).rsplit("/", 1)[-1]
        )
        if required:
            return f"{name}:{kind}!"
        return (
            f"{name}:{kind}" if "default" not in schema else f"{name}:{kind}={schema['default']!r}"
        )

    lines = []
    for tool in _tools():
        required = set(tool.input_schema.get("required", []))
        properties = tool.input_schema.get("properties", {})
        params = [describe(n, properties[n], n in required) for n in sorted(properties)]
        lines.append(f"{tool.name}({', '.join(params)})")
    return sorted(lines)
