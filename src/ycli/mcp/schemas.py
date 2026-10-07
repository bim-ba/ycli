"""``schema_get``: the schema of a tool's body that the tool's own listing leaves out.

A body whose schema would take its tool over ``SCHEMA_BUDGET_BYTES`` is listed as a free-form
object (:class:`ycli.yandex.mcp.OverBudget`) that names its model. This tool serves that model
and each definition it refers to, one at a time, so an agent reads only the part it needs.

It keeps no map of its own: the index is read from the listing of the server it is mounted on.
"""

from __future__ import annotations

import difflib
import pkgutil
from typing import TYPE_CHECKING, Annotated, Any

from fastmcp.exceptions import ToolError
from pydantic import Field, TypeAdapter

from ycli.yandex.mcp import RO, SCHEMA_ADDRESS, new_server
from ycli.yandex.models import APIModel

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from fastmcp import FastMCP
    from fastmcp.tools.base import Tool


class SchemaDefinition(APIModel):
    """One definition of a body's schema: a model, or the named union of several."""

    service: str = Field(description="The service whose tools take it, e.g. `forms`.")
    name: str = Field(description="The definition's name.")
    definition: dict[str, Any] = Field(
        description="Its JSON schema. A `$ref` of `#/$defs/<name>` is another definition of the "
        "same service: read it with the same tool."
    )


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


def schema_server(list_tools: Callable[[], Awaitable[Sequence[Tool]]]) -> FastMCP:
    """The server of ``schema_get`` for the root server whose tools ``list_tools`` lists.

    The index is built at the first call and kept: the tools a server serves do not change
    after it starts.
    """
    server = new_server("schema")
    index: dict[str, dict[str, dict[str, Any]]] = {}

    @server.tool(name="get", annotations={**RO, "title": "Read the schema of a tool's body"})
    async def get(
        service: Annotated[str, Field(description="The service of the tool, e.g. `forms`.")],
        name: Annotated[
            str, Field(description="The definition to read, as the tool's parameter names it.")
        ],
    ) -> SchemaDefinition:
        """Read one definition of a body that its tool lists as a free-form object.

        Such a parameter says in its description which definition to start from. The answer
        refers to others as ``#/$defs/<name>``: read those with this tool too, only the ones the
        task needs.
        """
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

    return server
