"""Listing transforms: a lighter ``tools/list``, and prompts and resources that follow their tools.

``tools/list`` of the full server is ~1.9 MB, 71% of it output schemas. The MCP spec makes
``outputSchema`` optional and a call still returns ``structuredContent`` without one, so the
listing drops it, and strips the doctest blocks that docstrings (the tool's and its request
models') carry for the Python SDK.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from fastmcp.server.transforms import Transform
from fastmcp.server.transforms.visibility import is_enabled

from ycli.yandex.mcp import NEEDS_TOOLS, REPEATS_TOOL, WRITE_TAG

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from fastmcp.prompts.base import Prompt
    from fastmcp.resources.template import ResourceTemplate
    from fastmcp.server.transforms import (
        GetPromptNext,
        GetResourceTemplateNext,
        GetToolNext,
    )
    from fastmcp.tools.base import Tool
    from fastmcp.utilities.versions import VersionSpec

_EXAMPLE_HEADER = re.compile(r"\s*Examples?:\s*$")
_DOCTEST_PROMPT = re.compile(r"\s*>>>")


def strip_examples(description: str) -> str:
    r"""``description`` without its ``Example:`` blocks and bare doctests.

    A block is the header line plus every indented or blank line after it; a bare doctest is a
    ``>>>`` line with the output lines that follow, up to the next blank line.

    Args:
        description: A tool or schema field description.

    Returns:
        The description without its examples.

    Examples:
        >>> strip_examples("Get an issue.\n\nExample:\n    >>> get('A-1')\n    'A-1'")
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
    r"""``schema`` with every ``description`` string passed through :func:`strip_examples`.

    Request models put their docstring, doctest included, into the input schema.

    Args:
        schema: A JSON schema, or any part of one.

    Returns:
        ``schema`` with every description stripped of its examples.

    Examples:
        >>> strip_schema_examples(
        ...     {"properties": {"body": {"description": "A body.\n\nExample:\n    x"}}}
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

    Only the listing changes: ``get_tool`` is untouched, so a call still returns
    ``structuredContent``, shaped by the tool's return type. Nothing checks it against the
    output schema, though: that check is the client's, made with the schema the listing gave
    it, and this listing gives none.
    """

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        """The tools with ``outputSchema`` dropped and doctest blocks stripped from their texts."""
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


class DerivedTags(Transform):
    """Tags every tool with its service and, when it is not read-only, with ``write``.

    The visibility filters match tags, and a tool already states both facts: its service is the
    namespace it is mounted under, its effect is ``readOnlyHint``. Deriving the tags here keeps
    one statement of each, so the two cannot disagree. It must be the first transform: the
    filters added after it read what it wrote.
    """

    @staticmethod
    def _tagged(tool: Tool) -> Tool:
        # A tool with no annotations counts as a write: hidden by ``--read-only``, never leaked.
        reads = tool.annotations is not None and tool.annotations.read_only_hint is True
        tags = {tool.name.partition("_")[0]} | (set() if reads else {WRITE_TAG})
        return tool.model_copy(update={"tags": tool.tags | tags})

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        """The tools, each with its derived tags."""
        return [self._tagged(tool) for tool in tools]

    async def get_tool(
        self, name: str, call_next: GetToolNext, *, version: VersionSpec | None = None
    ) -> Tool | None:
        """The tool ``name`` with its derived tags."""
        tool = await call_next(name, version=version)
        return None if tool is None else self._tagged(tool)


class UnknownToolError(ValueError):
    """A tool name in the selection that no mounted service serves."""


class ServedWithTheirTools(Transform):
    """Offers a prompt or a resource template only when the tools it is made of are served.

    A prompt lists the tools its text names (``NEEDS_TOOLS``) and a resource template the read
    tool it repeats (``REPEATS_TOOL``). One rule then covers every selection flag: with
    ``--read-only`` a prompt that ends in a write disappears with its write tool, and with
    ``--toolsets wiki`` so does a prompt that reads Tracker.

    It sits before the search transform, so the tools it sees are the real ones. It learns them
    from one listing it asks for itself: FastMCP also runs ``list_tools`` at startup over the
    task-capable tools only, and that list says nothing about what is served.
    """

    def __init__(self, list_tools: Callable[[], Awaitable[object]]) -> None:
        self._list_tools = list_tools
        self._asking = False
        self._served: frozenset[str] | None = None

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        """The tools unchanged; the enabled ones are remembered when this transform asked."""
        if self._asking:
            self._served = frozenset(tool.name for tool in tools if is_enabled(tool))
        return tools

    async def served(self) -> frozenset[str]:
        """The names of the tools this server serves (the selection never changes)."""
        if self._served is None:
            self._asking = True
            try:
                await self._list_tools()
            finally:
                self._asking = False
        assert self._served is not None  # the listing above went through list_tools
        return self._served

    async def _offered(self, component: Prompt | ResourceTemplate) -> bool:
        meta = component.meta or {}
        needed = {*meta.get(NEEDS_TOOLS, ()), *filter(None, [meta.get(REPEATS_TOOL)])}
        return needed <= await self.served()

    async def list_prompts(self, prompts: Sequence[Prompt]) -> Sequence[Prompt]:
        """The prompts whose every tool is served."""
        return [prompt for prompt in prompts if await self._offered(prompt)]

    async def get_prompt(
        self, name: str, call_next: GetPromptNext, *, version: VersionSpec | None = None
    ) -> Prompt | None:
        """The prompt ``name``, or ``None`` when a tool it names is not served."""
        prompt = await call_next(name, version=version)
        return prompt if prompt is not None and await self._offered(prompt) else None

    async def list_resource_templates(
        self, templates: Sequence[ResourceTemplate]
    ) -> Sequence[ResourceTemplate]:
        """The resource templates whose read tool is served."""
        return [template for template in templates if await self._offered(template)]

    async def get_resource_template(
        self,
        uri: str,
        call_next: GetResourceTemplateNext,
        *,
        version: VersionSpec | None = None,
    ) -> ResourceTemplate | None:
        """The template for ``uri``, or ``None`` when the read tool it repeats is not served."""
        template = await call_next(uri, version=version)
        return template if template is not None and await self._offered(template) else None
