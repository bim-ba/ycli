"""What the checks of several invariants share: where the code is, and how it is read."""

from __future__ import annotations

import ast
import asyncio
import re
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


_VIOLATION_RE = re.compile(r"\s*# violation\((?P<rule>[a-z0-9-]+)\): \S")
# The rules a marker may name besides an invariant (``arch-N``), and where each is stated:
# a section of docs/conventions/resources.md, or the script that holds the rule.
CONVENTION_RULES = {
    "naming": "7. Naming an operation",
    "api-drift": "scripts/api_drift.py: a body field that differs from the published API",
    "value-set": "1. Every model inherits `APIModel`: A field with a set of values",
    "as-given": "6. Writing a client and its CLI commands (ycli sends what the caller gave)",
}


def _below_the_comment(lines: list[str], index: int) -> int:
    """The index of the first line after the comment block that starts at ``index``."""
    below = index + 1
    while below < len(lines) and lines[below].lstrip().startswith("#"):
        below += 1
    return below


def violation_markers(source: str, rule: str) -> dict[int, int]:
    r"""The ``# violation(<rule>): <reason>`` markers of ``source``: explained line -> marker line.

    A marker stands alone on a comment line; its reason may run on over the comment lines right
    below it, and it explains the first line of code after them.
    ``"# violation(arch-9): own syntax\n# of the option\nraise E\n"`` and ``"arch-9"`` give
    ``{3: 1}``; a marker of another rule gives nothing.
    """
    lines = source.splitlines()
    found: dict[int, int] = {}
    for index, line in enumerate(lines):
        match = _VIOLATION_RE.match(line)
        if match is None or match["rule"] != rule:
            continue
        below = _below_the_comment(lines, index)
        found[below + 1] = index + 1
    return found


def unexplained(findings: list[tuple[int, str]], source: str, rule: str, path: str) -> list[str]:
    """Findings (line, text) with no marker of ``rule`` above them, and such markers above none."""
    markers = violation_markers(source, rule)
    lines = {line for line, _ in findings}
    return [text for line, text in findings if line not in markers] + [
        f"{path}:{marker}: violation({rule}) marks nothing the check finds"
        for line, marker in sorted(markers.items())
        if line not in lines
    ]


def malformed_markers(source: str) -> list[str]:
    """What is wrong with the form of the markers of ``source``, one line per marker.

    The form: a comment line of its own, ``# violation(<rule>): <reason>``, right above a line
    of code, where the rule is ``arch-1`` .. ``arch-9`` or a name in ``CONVENTION_RULES``.
    """
    lines = source.splitlines()
    wrong = []
    for index, line in enumerate(lines):
        if "violation(" not in line.partition("#")[2]:
            continue
        match = _VIOLATION_RE.match(line)
        if match is None:
            wrong.append(f"{index + 1}: not `# violation(<rule>): <reason>` on a line of its own")
            continue
        rule = match["rule"]
        if not re.fullmatch(r"arch-[1-9]", rule) and rule not in CONVENTION_RULES:
            wrong.append(f"{index + 1}: unknown rule {rule!r}")
        below = _below_the_comment(lines, index)
        if below == len(lines) or not lines[below].strip():
            wrong.append(f"{index + 1}: no line of code right below")
    return wrong
