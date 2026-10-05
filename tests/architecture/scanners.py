"""What the checks of several invariants share: where the code is, and how it is read."""

from __future__ import annotations

import ast
import asyncio
from pathlib import Path

from fastmcp import Client

from tests.full_server import mcp as root_mcp
from ycli.yandex.registry import SERVICES

SRC = Path(__file__).resolve().parents[2] / "src" / "ycli"
YANDEX = SRC / "yandex"
DOMAINS = tuple(service.name for service in SERVICES)


def _mcp_tools():
    async def go():
        async with Client(root_mcp) as c:
            return await c.list_tools()

    return asyncio.run(go())


def _probe_tools(register):
    """The tools of a throwaway server that ``register`` fills."""
    from fastmcp import FastMCP

    server = FastMCP("probe")
    register(server)

    async def listed():
        async with Client(server) as client:
            return await client.list_tools()

    return asyncio.run(listed())


def _import_aliases(tree: ast.AST) -> dict[str, str]:
    """Each imported local name -> the dotted name it stands for.

    ``from rich import print as rprint`` gives ``{"rprint": "rich.print"}``; ``import pprint``
    gives ``{"pprint": "pprint"}``; ``import yaml as y`` gives ``{"y": "yaml"}``.
    """
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.partition(".")[0]
                aliases[alias.asname or top] = alias.name if alias.asname else top
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


def _dotted(expr: ast.expr, aliases: dict[str, str]) -> str:
    """The dotted name ``expr`` refers to, imports resolved; ``""`` if it is not a name chain.

    ``rprint`` -> ``rich.print``; ``sys.__stdout__.write`` -> ``sys.__stdout__.write``;
    ``Console().print`` -> ``""`` (the inner ``Console()`` call is judged on its own).
    """
    parts: list[str] = []
    while isinstance(expr, ast.Attribute):
        parts.append(expr.attr)
        expr = expr.value
    if not isinstance(expr, ast.Name):
        return ""
    parts.append(aliases.get(expr.id, expr.id))
    return ".".join(reversed(parts))
