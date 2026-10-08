"""``schema_get``: the schemas a tool's own listing leaves out, one definition at a time.

A body whose schema would take its tool over ``SCHEMA_BUDGET_BYTES`` is listed as a free-form
object (:class:`ycli.yandex.mcp.OverBudget`) that names its model. This tool serves that model
and each definition it refers to, one at a time, so an agent reads only the part it needs.

The reply of a tool is not listed at all (the listing would be megabytes); this tool serves it
the same way, addressed by the tool: its top schema, then a part by its name.

It keeps no map of its own: the index is read from the server it is mounted on.
"""

from __future__ import annotations

import difflib
import pkgutil
from typing import TYPE_CHECKING, Annotated, Any

from fastmcp.exceptions import ToolError
from pydantic import Field, RootModel, TypeAdapter

from ycli.yandex.mcp import ALWAYS_LOAD, RO, SCHEMA_ADDRESS, new_server
from ycli.yandex.models import APIModel, KindByOwnField, RequestBody

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from fastmcp import FastMCP
    from fastmcp.tools.base import Tool


class SchemaDefinition(APIModel):
    """One definition of a body's schema: a model, or the named union of several."""

    service: str = Field(description="The service whose tools take it, e.g. `forms`.")
    name: str = Field(description="The definition's name; for a tool's reply, the tool's.")
    definition: dict[str, Any] = Field(
        description="Its JSON schema. A `$ref` of `#/$defs/<name>` is another definition: of "
        "the same service for a body, of the same tool for a reply. Read it with this tool."
    )


class _OfABody(RequestBody):
    service: str = Field(description="The service of the tool.")
    name: str = Field(description="The definition to read.")


class _OfAReply(RequestBody):
    tool: str = Field(description="The tool whose reply to read.")
    name: str | None = Field(default=None, description="A part of the reply, by its name.")


class Asked(RootModel, hide_input_in_errors=True):
    """What ``schema_get`` is asked for: a definition of a body, or the reply of a tool.

    Examples:
        >>> type(Asked.model_validate({"tool": "tracker_issues_get"}).root).__name__
        '_OfAReply'
        >>> Asked.model_validate({"name": "Issue"})
        Traceback (most recent call last):
            ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for Asked
          give exactly one of: service, tool [type=one_kind]
    """

    root: Annotated[_OfABody | _OfAReply, KindByOwnField()]


def definitions(tools: Sequence[Tool]) -> dict[str, dict[str, dict[str, Any]]]:
    """Every definition the over-budget parameters of ``tools`` name: service → name → schema.

    A tool's service is the namespace it is mounted under, the first word of its name. Within
    a service a name means one definition: two bodies may share a definition, and two
    different ones under one name stop the index, since an agent asking for the name would
    be handed the wrong schema.

    Args:
        tools: The tools a server lists.

    Returns:
        The definitions by service and name; empty when no parameter is marked.

    Raises:
        ValueError: Two definitions of one service have the same name and differ.
    """
    found: dict[str, dict[str, dict[str, Any]]] = {}
    for tool in tools:
        for parameter in tool.parameters.get("properties", {}).values():
            address = parameter.get(SCHEMA_ADDRESS)
            if address is None:
                continue
            schema = TypeAdapter(pkgutil.resolve_name(address)).json_schema()
            nested = schema.pop("$defs", {})
            service = tool.name.partition("_")[0]
            known = found.setdefault(service, {})
            for name, definition in {address.rpartition(":")[2]: schema, **nested}.items():
                if known.setdefault(name, definition) != definition:
                    raise ValueError(
                        f"two definitions named {name!r} in {service} differ; "
                        f"the second comes with {address} ({tool.name})"
                    )
    return found


def schema_server(
    list_tools: Callable[[], Awaitable[Sequence[Tool]]],
    get_tool: Callable[[str], Awaitable[Tool | None]],
) -> FastMCP:
    """The server of ``schema_get`` for the root server that ``list_tools`` and ``get_tool`` read.

    The index of bodies is built at the first call and kept: the tools a server serves do not
    change after it starts. A reply is read from its tool when asked for.
    """
    server = new_server("schema")
    index: dict[str, dict[str, dict[str, Any]]] = {}

    async def of_a_body(service: str, name: str) -> SchemaDefinition:
        if not index:
            index.update(definitions(await list_tools()))
        if not index:
            raise ToolError("This server serves no schema on request: every tool lists its own.")
        known = index.get(service)
        if known is None:
            raise ToolError(f"No schema of {service!r}; services with schemas: {', '.join(index)}.")
        if name not in known:
            near = difflib.get_close_matches(name, known, n=8, cutoff=0.4) or sorted(known)[:8]
            raise ToolError(
                f"No definition {name!r} in {service}; did you mean: {', '.join(near)}?"
            )
        return SchemaDefinition(service=service, name=name, definition=known[name])

    async def of_a_reply(tool: str, name: str | None) -> SchemaDefinition:
        names = [listed.name for listed in await list_tools()]
        held = await get_tool(tool) if tool in names else None
        if held is None:
            near = difflib.get_close_matches(tool, names, n=8, cutoff=0.4) or sorted(names)[:8]
            raise ToolError(f"No tool {tool!r}; did you mean: {', '.join(near)}?")
        schema = dict(held.output_schema or {})
        parts = schema.pop("$defs", {})
        if schema.pop("x-fastmcp-wrap-result", False):
            # FastMCP wraps what is not an object; the schema of what the tool returns is inside.
            schema = schema["properties"]["result"]
        if name is not None and name not in parts:
            near = difflib.get_close_matches(name, parts, n=8, cutoff=0.4) or sorted(parts)[:8]
            raise ToolError(
                f"No definition {name!r} in the reply of {tool}; did you mean: {', '.join(near)}?"
            )
        return SchemaDefinition(
            service=tool.partition("_")[0],
            name=name or tool,
            definition=schema if name is None else parts[name],
        )

    @server.tool(
        name="get",
        annotations={**RO, "title": "Read the schema of a tool's body or reply"},
        meta=ALWAYS_LOAD,
    )
    async def get(
        service: Annotated[
            str | None, Field(description="For a body: the service of the tool, e.g. `forms`.")
        ] = None,
        name: Annotated[
            str | None,
            Field(
                description="The definition to read: for a body, as the tool's parameter names "
                "it; for a reply, a part of it (left out: the reply itself)."
            ),
        ] = None,
        tool: Annotated[
            str | None,
            Field(
                description="For a reply: the tool whose answer to read, e.g. `forms_surveys_get`."
            ),
        ] = None,
    ) -> SchemaDefinition:
        """Read one definition: of a body its tool lists as a free-form object, or of a reply.

        A body: give ``service`` and ``name``; such a parameter says in its description which
        definition to start from. A reply, to know what a tool answers before calling it: give
        ``tool``, then ``tool`` and ``name`` for a part. The answer refers to others as
        ``#/$defs/<name>``: read those with this tool too, only the ones the task needs.
        """
        given = {"service": service, "name": name, "tool": tool}
        asked = Asked.model_validate({key: value for key, value in given.items() if value}).root
        if isinstance(asked, _OfAReply):
            return await of_a_reply(asked.tool, asked.name)
        return await of_a_body(asked.service, asked.name)

    return server
