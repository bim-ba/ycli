"""Every MCP tool carries the read/idempotent/open-world hints + a title; servers have instructions."""  # noqa: E501

from __future__ import annotations

import asyncio
from typing import Annotated, Any

from fastmcp import Client
from pydantic import Field

from tests.full_server import mcp as root_mcp
from tests.full_server import tools_with_output_schemas
from ycli.yandex.models import APIModel
from ycli.yandex.registry import SERVICES


def _tools():
    async def go():
        async with Client(root_mcp) as client:
            return await client.list_tools()

    return asyncio.run(go())


def test_every_tool_has_hints_and_title():
    tools = _tools()
    assert tools
    for tool in tools:
        ann = tool.annotations
        assert ann is not None, tool.name
        assert isinstance(ann.read_only_hint, bool), f"{tool.name} must declare readOnlyHint"
        assert ann.open_world_hint is True, tool.name
        if ann.read_only_hint:
            assert ann.idempotent_hint is True, tool.name
        else:
            # Writes declare their remaining hints explicitly — the MCP-spec default
            # for an unannotated tool is destructiveHint=true (see ARCH-3).
            assert isinstance(ann.destructive_hint, bool), (
                f"{tool.name} write tool must declare destructiveHint"
            )
            assert isinstance(ann.idempotent_hint, bool), (
                f"{tool.name} write tool must declare idempotentHint"
            )
        assert ann.title and ann.title.strip(), f"{tool.name} has no title"


def _undescribed_parameters(tools) -> list[str]:
    """``tool.parameter`` for every input property whose description is missing or blank."""
    return [
        f"{tool.name}.{name}"
        for tool in tools
        for name, schema in tool.input_schema.get("properties", {}).items()
        if not str(schema.get("description", "")).strip()
    ]


def test_every_tool_parameter_has_a_description():
    """An agent reads these to fill the call: a bare ``key`` or ``queue_id`` is a guess."""
    assert _undescribed_parameters(_tools()) == []


def test_the_parameter_description_check_bites():
    from fastmcp import FastMCP

    server = FastMCP("probe")

    @server.tool
    def probe(
        bare: str,
        blank: Annotated[str, Field(description="  ")],
        ok: Annotated[str, Field(description="Fine.")],
    ) -> str:
        """Probe."""
        return ""

    async def listed():
        async with Client(server) as client:
            return await client.list_tools()

    tools = asyncio.run(listed())
    assert _undescribed_parameters(tools) == ["probe.bare", "probe.blank"]


def test_servers_have_instructions():
    for server in (root_mcp, *(service.mcp_server() for service in SERVICES)):
        assert server.instructions and server.instructions.strip()


def _subclasses(cls: type[APIModel]) -> list[type[APIModel]]:
    return [cls, *(sub for direct in cls.__subclasses__() for sub in _subclasses(direct))]


def _property_names(schema: Any) -> set[str]:
    """Every property name anywhere in a JSON schema, nested models included."""
    if isinstance(schema, list):
        return {name for item in schema for name in _property_names(item)}
    if not isinstance(schema, dict):
        return set()
    nested = {name for value in schema.values() for name in _property_names(value)}
    return set(schema.get("properties", {})) | nested


def test_tool_output_uses_the_api_field_names():
    """MCP output keeps the wire names the CLI prints (``checklistItems``, not ``checklist_items``).

    Both surfaces mirror the Yandex API, so a field reads the same in the vendor docs, in
    ``ycli … -o json`` and in a tool result. fastmcp 4 serializes by attribute name unless the
    model says otherwise, which ``APIModel`` does with ``serialize_by_alias``. A Python name
    that is also some API's wire name (Wiki's ``created_at``) cannot be told apart, so it is
    left out of the check.
    """
    fields = [
        (name, field.alias or name)
        for model in _subclasses(APIModel)
        for name, field in model.model_fields.items()
    ]
    python_only = {name for name, wire in fields if name != wire} - {wire for _, wire in fields}
    offenders = {
        tool.name: sorted(leaked)
        for tool in asyncio.run(tools_with_output_schemas())  # the listing carries no schema
        if (leaked := _property_names(tool.output_schema) & python_only)
    }
    assert not offenders, offenders
