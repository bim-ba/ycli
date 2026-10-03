"""The lighter ``tools/list``: no output schemas, no doctest blocks, calls unchanged."""

import json

import pytest
from fastmcp import Client

from tests.full_server import mcp
from tests.hosts import TRACKER_BASE
from ycli.mcp.listing import strip_examples
from ycli.yandex.tracker.mcp.server import mcp as tracker_mcp


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("Get an issue.", "Get an issue."),
        ("Get an issue.\n\nExample:\n    >>> get('A-1')\n    'A-1'", "Get an issue."),
        ("Get.\n\nExamples:\n    >>> a\n    1\n\n    >>> b\n    2", "Get."),
        # Prose after the example block is kept.
        ("Get.\n\nExample:\n    >>> a\n    1\n\nNote: keep me.", "Get.\n\nNote: keep me."),
        # A bare doctest loses its output lines too, but not the paragraph after the blank line.
        ("Get.\n>>> a\n1\n\nMore.", "Get.\n\nMore."),
        ("Mentions Example: inline, no block.", "Mentions Example: inline, no block."),
        ("", ""),
    ],
)
def test_strip_examples(description, expected):
    assert strip_examples(description) == expected


async def test_the_source_schemas_do_carry_doctests():
    """Bite: without the transform request models list their doctests, so the strip is real."""
    raw = {tool.name: tool for tool in await tracker_mcp.list_tools()}
    assert any(">>>" in json.dumps(tool.parameters) for tool in raw.values())
    assert all(tool.output_schema for tool in raw.values())


async def test_the_listing_has_no_output_schema_and_no_doctest():
    async with Client(mcp) as client:
        tools = await client.list_tools()
    assert len(tools) > 300
    assert [tool.name for tool in tools if tool.output_schema is not None] == []
    assert [tool.name for tool in tools if ">>>" in (tool.description or "")] == []
    assert [tool.name for tool in tools if "Example:" in (tool.description or "")] == []
    # The request models' own docstrings reach the input schema; they are stripped too.
    assert [tool.name for tool in tools if ">>>" in json.dumps(tool.input_schema)] == []


async def test_a_call_still_returns_structured_content(api):
    """The schema leaves the listing, not the result: callers still get ``structuredContent``."""
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "ada", "uid": 7})
    async with Client(mcp) as client:
        listed = {tool.name: tool for tool in await client.list_tools()}
        assert listed["tracker_me_get"].output_schema is None
        result = await client.call_tool("tracker_me_get", {})
    assert result.structured_content is not None
    assert result.structured_content["login"] == "ada"


async def test_a_listing_keeps_what_else_a_client_reads():
    """Names, input schemas and annotations are untouched; only the two heavy parts go."""
    raw = {tool.name: tool for tool in await tracker_mcp.list_tools()}["issues_get"]
    light = {tool.name: tool for tool in await mcp.list_tools()}["tracker_issues_get"]
    assert light.parameters == raw.parameters
    assert light.annotations == raw.annotations
    assert light.tags == raw.tags
