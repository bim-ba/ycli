"""The lighter ``tools/list``: no output schemas, no doctest blocks, calls unchanged."""

import json

import pytest
from fastmcp import Client
from fastmcp.tools import Tool
from fastmcp.utilities.versions import VersionSpec
from mcp.types import ToolAnnotations

from tests.full_server import mcp
from tests.hosts import TRACKER_BASE
from ycli.mcp.listing import DerivedTags, GrantsSaid, strip_examples
from ycli.yandex.mcp import (
    DESTRUCTIVE,
    GRANTS_ACCESS,
    GRANTS_ACCESS_SAID,
    RO,
    WRITE,
    WRITE_TAG,
)
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
    assert light.tags == {"tracker"}  # derived at the root; the tool itself states none
    assert raw.tags == set()


def _tool(name: str, hints: dict[str, bool] | None) -> Tool:
    def probe() -> str:
        """Probe."""
        return ""

    annotations = None if hints is None else ToolAnnotations.model_validate(hints)
    return Tool.from_function(probe, name=name, annotations=annotations)


@pytest.mark.parametrize(
    ("name", "hints", "tags"),
    [
        ("tracker_issues_get", RO, {"tracker"}),
        ("wiki_pages_update", WRITE, {"wiki", WRITE_TAG}),
        ("forms_surveys_delete", DESTRUCTIVE, {"forms", WRITE_TAG}),
        ("status_get", RO, {"status"}),
        # No annotations: counted as a write, so ``--read-only`` hides it.
        ("tracker_unannotated", None, {"tracker", WRITE_TAG}),
    ],
)
async def test_tags_are_derived_from_the_name_and_the_read_only_hint(name, hints, tags):
    tool = _tool(name, hints)
    [listed] = await DerivedTags().list_tools([tool])
    assert listed.tags == tags

    async def held(name: str, *, version: VersionSpec | None = None) -> Tool | None:
        return tool

    found = await DerivedTags().get_tool(name, held)
    assert found is not None
    assert found.tags == tags


async def test_a_tool_the_server_does_not_hold_stays_absent():
    async def nothing(name: str, *, version: VersionSpec | None = None) -> Tool | None:
        return None

    assert await DerivedTags().get_tool("tracker_ghost", nothing) is None


async def test_a_tool_that_grants_access_says_so_in_words_once():
    """The mark is a key one client reads: the description says it for the others."""

    def grant() -> str:
        """Give a user a role."""
        return ""

    marked = Tool.from_function(grant, name="wiki_access_create", meta=GRANTS_ACCESS)
    plain = Tool.from_function(grant, name="wiki_access_list")
    said, untouched = await GrantsSaid().list_tools([marked, plain])
    assert said.description == f"Give a user a role.\n\n{GRANTS_ACCESS_SAID}"
    assert untouched is plain
    # A server mounted in another passes its tools through the transform twice.
    [again] = await GrantsSaid().list_tools([said])
    assert again is said

    async def held(name: str, *, version: VersionSpec | None = None) -> Tool | None:
        return marked if name == marked.name else None

    found = await GrantsSaid().get_tool(marked.name, held)
    assert found is not None and found.description == said.description
    assert await GrantsSaid().get_tool("wiki_ghost", held) is None
