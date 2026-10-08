"""Every MCP tool has a description and an output schema."""

import asyncio
import re
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from tests.architecture.scanners import _probe_tools
from tests.full_server import mcp, tools_with_output_schemas


def test_every_mcp_tool_has_description_and_output_schema():
    """Every tool has a docstring-derived description and a return-annotation-derived output schema.

    The docstring IS the client-facing description (the LLM's selector).
    The return type annotation IS the output schema (auto-derived by fastmcp).
    Both are required — omitting either makes the tool invisible or unusable to agents.
    See docs/conventions/resources.md §MCP tool-metadata standard.
    """
    tools = asyncio.run(tools_with_output_schemas())  # the listing itself carries none
    assert tools, "no MCP tools discovered"
    assert _undescribed_tools(tools) == []


def _undescribed_tools(tools) -> list[str]:
    """Tools with no docstring (→ description) or no return annotation (→ output schema)."""
    return [tool.name for tool in tools if not tool.description or tool.output_schema is None]


def test_the_description_and_output_schema_check_bites():
    def register(server):
        @server.tool
        def no_docstring() -> str:
            return ""

        @server.tool
        def no_return_type():
            """Probe."""

        @server.tool
        def complete() -> str:
            """Probe."""
            return ""

    assert sorted(_undescribed_tools(_probe_tools(register))) == ["no_docstring", "no_return_type"]


# What Claude Code does to a server's text and tools, from its documentation
# (https://code.claude.com/docs/en/mcp, read 2026-10-08): it "truncates each tool description
# and each server's instructions at 2,048 characters", silently; it excludes a tool whose
# top-level property names are not "1 to 64 characters long" of "ASCII letters and digits, `_`,
# `.`, and `-`", or whose schema is not valid against the JSON Schema draft 2020-12
# meta-schema; and a schema with `anyOf`, `oneOf` or `allOf` at its root is rewritten, or the
# tool skipped. The API takes a tool name that matches `^[a-zA-Z0-9_-]{1,128}$`
# (https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools).
TEXT_LIMIT = 2048
_TOOL_NAME = re.compile(r"[a-zA-Z0-9_-]{1,128}")
_PROPERTY_NAME = re.compile(r"[A-Za-z0-9_.-]{1,64}")
_ROOT_COMBINATORS = ("anyOf", "oneOf", "allOf")


def _lost_on_a_client(name: str, description: str | None, schema: dict[str, Any]) -> list[str]:
    """Why a client would cut the text of a tool short, or not show the tool at all."""
    problems = []
    if len(description or "") > TEXT_LIMIT:
        problems.append(f"{name}: the description is {len(description or '')} characters long")
    if not _TOOL_NAME.fullmatch(name):
        problems.append(f"{name}: the name is not one a client takes")
    problems += [
        f"{name}: `{combinator}` at the root of the input schema"
        for combinator in _ROOT_COMBINATORS
        if combinator in schema
    ]
    problems += [
        f"{name}: the property name {key!r} is not one a client takes"
        for key in schema.get("properties", {})
        if not _PROPERTY_NAME.fullmatch(key)
    ]
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as wrong:
        problems.append(f"{name}: the input schema is not a JSON Schema ({wrong.message})")
    return problems


def test_no_text_is_cut_and_no_tool_is_dropped_by_a_client():
    """Every description and the instructions fit, and every input schema is one a client takes."""
    tools = asyncio.run(mcp.list_tools())
    assert len(tools) > 400
    problems = [
        problem
        for tool in tools
        for problem in _lost_on_a_client(tool.name, tool.description, tool.parameters)
    ]
    assert problems == []
    assert 0 < len(mcp.instructions or "") <= TEXT_LIMIT


def test_the_check_of_what_a_client_loses_bites():
    """Prove-it, on a stand-in tool for each way a client loses one."""
    fine = {"type": "object", "properties": {"issue_key": {"type": "string"}}}
    assert _lost_on_a_client("tracker_issues_get", "Get an issue.", fine) == []
    assert _lost_on_a_client("tracker_issues_get", "x" * (TEXT_LIMIT + 1), fine) == [
        "tracker_issues_get: the description is 2049 characters long"
    ]
    assert _lost_on_a_client("tracker issues.get", "Get.", fine) == [
        "tracker issues.get: the name is not one a client takes"
    ]
    union = {"anyOf": [fine, {"type": "object", "properties": {"id": {"type": "integer"}}}]}
    assert _lost_on_a_client("a_get", "Get.", union) == [
        "a_get: `anyOf` at the root of the input schema"
    ]
    named = {"type": "object", "properties": {"issue key": {"type": "string"}, "k" * 65: {}}}
    assert _lost_on_a_client("a_get", "Get.", named) == [
        "a_get: the property name 'issue key' is not one a client takes",
        f"a_get: the property name '{'k' * 65}' is not one a client takes",
    ]
    (broken,) = _lost_on_a_client("a_get", "Get.", {"type": "object", "properties": []})
    assert broken.startswith("a_get: the input schema is not a JSON Schema (")
    # A combinator inside a property is taken as it is.
    nested = {
        "type": "object",
        "properties": {"id": {"anyOf": [{"type": "string"}, {"type": "null"}]}},
    }
    assert _lost_on_a_client("a_get", "Get.", nested) == []
