"""Deterministic enumerators of ycli's public surface: the CLI and what the MCP server offers."""

import asyncio
import hashlib
import json
from typing import Any

import typer
import typer.main
from fastmcp import Client

from tests.full_server import mcp, tools_with_output_schemas
from ycli.cli.app import app
from ycli.cli.lazy import LazyGroup


def _walk(command, context: typer.Context, prefix: str) -> list[tuple[str, Any]]:
    """Every ``(path, command)`` under ``command``; list/get_command, as the root is lazy."""
    out: list[tuple[str, Any]] = []
    if not hasattr(command, "list_commands"):
        return out
    for name in sorted(command.list_commands(context)):
        sub = command.get_command(context, name)
        if isinstance(sub, LazyGroup):  # the stand-in lists a sub-app; walk the real one
            sub = sub.load()
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
    """``--limit:INTEGER=0`` / ``KEY:TEXT!`` — name, type, then ``!`` (required) or the default."""
    longest_opt = max(param.opts, key=len)
    label = str(longest_opt) if param.param_type_name == "option" else str(param.name).upper()
    label = f"{label}:{param.type.name.upper()}"
    if param.required:
        return f"{label}!"
    return label if param.default is None else f"{label}={param.default!r}"


def cli_leaves() -> dict[str, Any]:
    """Every leaf command by space-joined path, e.g. ``'tracker issues get'``."""
    return {path: command for path, command in _commands() if not hasattr(command, "list_commands")}


def cli_signature(path: str, command: Any) -> str:
    """One leaf command with its parameters, e.g. ``tracker issues get: KEY:TEXT!``."""
    return f"{path}: {' '.join(sorted(_cli_param(p) for p in command.params))}".rstrip(": ")


def cli_signatures() -> list[str]:
    """Each leaf command with its parameters."""
    return [
        cli_signature(path, command)
        for path, command in _commands()
        if not hasattr(command, "list_commands")
    ]


def _tools() -> list:
    async def go() -> list:
        async with Client(mcp) as client:
            return await client.list_tools()

    return asyncio.run(go())


def mcp_signature(tool: Any) -> str:
    """One MCP tool with typed parameters, e.g. ``tracker_issues_get(key:string!)``."""

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

    required = set(tool.input_schema.get("required", []))
    properties = tool.input_schema.get("properties", {})
    params = [describe(n, properties[n], n in required) for n in sorted(properties)]
    return f"{tool.name}({', '.join(params)})"


def mcp_signatures() -> list[str]:
    """Each MCP tool with typed parameters."""
    return sorted(mcp_signature(tool) for tool in _tools())


def mcp_prompts_and_resources() -> list[str]:
    """Each MCP prompt with its arguments (``!`` = required), then each resource address."""

    async def go() -> list[str]:
        async with Client(mcp) as client:
            prompts = [
                f"prompt {prompt.name}("
                + ", ".join(
                    f"{argument.name}{'!' if argument.required else ''}"
                    for argument in prompt.arguments or []
                )
                + ")"
                for prompt in await client.list_prompts()
            ]
            resources = [f"resource {resource.uri}" for resource in await client.list_resources()]
            templates = [
                f"resource {template.uri_template}"
                for template in await client.list_resource_templates()
            ]
        return [*sorted(prompts), *sorted([*resources, *templates])]

    return asyncio.run(go())


def mcp_output_schemas() -> list[str]:
    """``<tool> <sha256 of its output schema>`` per tool: any change to what a tool returns.

    The listing drops output schemas (``LightListing``), so they are read from the server.
    """
    tools = asyncio.run(tools_with_output_schemas())
    return [
        f"{tool.name} "
        + hashlib.sha256(
            json.dumps(tool.output_schema, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()[:16]
        for tool in sorted(tools, key=lambda tool: tool.name)
    ]
