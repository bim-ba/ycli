"""Listing transforms: a lighter ``tools/list`` and a check that selected tool names exist.

``tools/list`` of the full server is ~1.9 MB, 71% of it output schemas. The MCP spec makes
``outputSchema`` optional and a call still returns ``structuredContent`` without one, so the
listing drops it, and strips the doctest blocks that docstrings (the tool's and its request
models') carry for the Python SDK.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from fastmcp.server.transforms import Transform

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fastmcp.tools.base import Tool

_EXAMPLE_HEADER = re.compile(r"\s*Examples?:\s*$")
_DOCTEST_PROMPT = re.compile(r"\s*>>>")


def strip_examples(description: str) -> str:
    """``description`` without its ``Example:`` blocks and bare doctests.

    A block is the header line plus every indented or blank line after it; a bare doctest is a
    ``>>>`` line with the output lines that follow, up to the next blank line.

    Example:
        >>> strip_examples("Get an issue.\\n\\nExample:\\n    >>> get('A-1')\\n    'A-1'")
        'Get an issue.'
    """
    kept: list[str] = []
    in_block = in_doctest = False
    for line in description.splitlines():
        if in_doctest and line.strip():
            continue
        in_doctest = False
        if _EXAMPLE_HEADER.fullmatch(line):
            in_block = True
            continue
        if in_block and (not line.strip() or line[0] in " \t"):
            continue
        in_block = False
        if _DOCTEST_PROMPT.match(line):
            in_doctest = True
            continue
        kept.append(line)
    return "\n".join(kept).rstrip()


def strip_schema_examples(schema: Any) -> Any:
    """``schema`` with every ``description`` string passed through :func:`strip_examples`.

    Request models put their docstring, doctest included, into the input schema.

    Example:
        >>> strip_schema_examples(
        ...     {"properties": {"body": {"description": "A body.\\n\\nExample:\\n    x"}}}
        ... )
        {'properties': {'body': {'description': 'A body.'}}}
    """
    if isinstance(schema, dict):
        return {
            key: strip_examples(value)
            if key == "description" and isinstance(value, str)
            else strip_schema_examples(value)
            for key, value in schema.items()
        }
    if isinstance(schema, list):
        return [strip_schema_examples(item) for item in schema]
    return schema


class LightListing(Transform):
    """Lists tools without ``outputSchema`` and without doctest blocks in their texts.

    Only the listing changes: ``get_tool`` is untouched, so a call still validates its result
    against the tool's full output schema and returns ``structuredContent``.
    """

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        return [
            tool.model_copy(
                update={
                    "output_schema": None,
                    "description": strip_examples(tool.description or ""),
                    "parameters": strip_schema_examples(tool.parameters),
                }
            )
            for tool in tools
        ]


class UnknownToolError(ValueError):
    """A tool name in the selection that no mounted service serves."""


class KnownTools(Transform):
    """Fails the listing when a requested tool name matches no tool.

    FastMCP's ``enable`` / ``disable`` silently match nothing for an unknown name, so a typo in
    ``--tools`` would hide or show the wrong set without a word.
    """

    def __init__(self, requested: frozenset[str]) -> None:
        self._requested = requested

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        unknown = sorted(self._requested - {tool.name for tool in tools})
        if unknown:
            raise UnknownToolError(f"unknown tool name(s): {', '.join(unknown)}")
        return tools
