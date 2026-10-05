"""Which tools a server serves for each selection: toolsets, profiles, exclusions, read-only."""

import subprocess
import sys

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tests.full_server import mcp as full_server
from tests.hosts import TRACKER_BASE
from ycli.mcp.listing import UnknownToolError
from ycli.mcp.profiles import ALWAYS_SERVED, CORE_TOOLS, SCHEMA_TOOL, STATUS_TOOL
from ycli.mcp.selection import CORE, Selection, split_names
from ycli.mcp.server import build_server, check_tool_names
from ycli.yandex.mcp import WRITE_TAG


async def served(selection: Selection) -> set[str]:
    return {tool.name for tool in await build_server(selection).list_tools()}


async def every_tool() -> dict[str, set[str]]:
    """Every tool of the full server, with its tags."""
    return {tool.name: set(tool.tags) for tool in await full_server.list_tools()}


def test_split_names_trims_and_drops_blanks():
    assert split_names(" a, b ,,c ") == ("a", "b", "c")
    assert split_names("") == ()


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"toolsets": ("nope",)},
            "unknown toolset.*nope.*valid: tracker, wiki, forms, datalens, core, all",
        ),
        ({"toolsets": ()}, "none given"),
        ({"exclude_tools": (STATUS_TOOL,)}, "always served"),
        ({"exclude_tools": (SCHEMA_TOOL,)}, "always served"),
        ({"tools": ("nope_get",)}, "unknown tool 'nope_get'"),
        ({"exclude_tools": ("get",)}, "unknown tool 'get'"),
    ],
)
def test_a_bad_selection_fails_at_construction(kwargs, message):
    with pytest.raises(ValueError, match=message):
        Selection(**kwargs)


@pytest.mark.parametrize(
    ("selection", "services"),
    [
        (Selection(), ("tracker", "wiki", "forms", "datalens")),
        (Selection(toolsets=("wiki",)), ("wiki",)),
        (Selection(toolsets=("forms", "tracker")), ("tracker", "forms")),
        (Selection(toolsets=(CORE,)), ("tracker", "wiki", "forms")),
        # A tool or exclusion from another service mounts it, so the name can be checked.
        (Selection(toolsets=("wiki",), tools=("tracker_issues_get",)), ("tracker", "wiki")),
        (Selection(toolsets=("wiki",), exclude_tools=("forms_surveys_get",)), ("wiki", "forms")),
        (Selection(toolsets=("wiki",), tools=(STATUS_TOOL,)), ("wiki",)),
    ],
)
def test_services_are_the_ones_the_selection_needs(selection, services):
    assert selection.services() == services


def test_only_the_selected_services_are_imported():
    """``--toolsets wiki`` never imports Tracker or Forms (the point of mounting by selection)."""
    code = (
        "import sys\n"
        "from ycli.mcp.selection import Selection\n"
        "from ycli.mcp.server import build_server\n"
        "build_server(Selection(toolsets=('wiki',)))\n"
        "assert 'ycli.yandex.wiki.mcp.server' in sys.modules\n"
        "assert 'ycli.yandex.tracker.mcp' not in sys.modules\n"
        "assert 'ycli.yandex.forms.mcp' not in sys.modules\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


async def test_default_serves_every_tool():
    assert await served(Selection()) == set(await every_tool())


@pytest.mark.parametrize("service", ["tracker", "wiki", "forms"])
async def test_a_service_toolset_serves_that_service_and_status(service):
    tools = await every_tool()
    expected = {name for name in tools if name.startswith(f"{service}_")} | {*ALWAYS_SERVED}
    assert await served(Selection(toolsets=(service,))) == expected


async def test_several_toolsets_union():
    names = await served(Selection(toolsets=("wiki", "forms")))
    assert {n.split("_")[0] for n in names} == {"wiki", "forms", "status", "schema"}


def test_core_profile_is_curated_and_exists_in_the_full_server():
    assert 30 <= len(CORE_TOOLS) <= 50
    assert {*ALWAYS_SERVED} <= CORE_TOOLS


async def test_core_profile_names_all_exist():
    assert set(await every_tool()) >= CORE_TOOLS


async def test_core_serves_exactly_the_profile():
    assert await served(Selection(toolsets=(CORE,))) == CORE_TOOLS


async def test_core_has_write_tools_for_everyday_edits():
    tools = await every_tool()
    writes = {name for name in CORE_TOOLS if WRITE_TAG in tools[name]}
    assert {"tracker_issues_create", "tracker_comments_create", "wiki_pages_update"} <= writes
    # Nothing destructive or administrative in the everyday profile.
    assert not {n for n in CORE_TOOLS if n.endswith(("_delete", "_clear"))}


async def test_tools_add_beyond_the_toolset():
    names = await served(Selection(toolsets=("wiki",), tools=("tracker_issues_get",)))
    assert "tracker_issues_get" in names
    assert "tracker_issues_list" not in names
    assert "wiki_pages_get" in names


async def test_tools_add_to_core():
    names = await served(Selection(toolsets=(CORE,), tools=("forms_surveys_create",)))
    assert names == CORE_TOOLS | {"forms_surveys_create"}


async def test_core_with_a_whole_service():
    tools = await every_tool()
    names = await served(Selection(toolsets=(CORE, "forms")))
    assert names == CORE_TOOLS | {n for n in tools if n.startswith("forms_")}


async def test_exclude_removes_from_a_toolset_and_from_all():
    names = await served(Selection(toolsets=(CORE,), exclude_tools=("tracker_issues_move",)))
    assert names == CORE_TOOLS - {"tracker_issues_move"}
    assert "tracker_issues_move" not in await served(
        Selection(exclude_tools=("tracker_issues_move",))
    )


async def test_exclude_beats_tools():
    names = await served(
        Selection(
            toolsets=("wiki",), tools=("tracker_issues_get",), exclude_tools=("tracker_issues_get",)
        )
    )
    assert "tracker_issues_get" not in names


async def test_read_only_hides_every_write_tool():
    tools = await every_tool()
    names = await served(Selection(read_only=True))
    assert names == {name for name, tags in tools.items() if WRITE_TAG not in tags}


async def test_read_only_beats_tools_and_core():
    names = await served(
        Selection(toolsets=(CORE,), tools=("tracker_queues_delete",), read_only=True)
    )
    tools = await every_tool()
    assert "tracker_queues_delete" not in names
    assert names == {n for n in CORE_TOOLS if WRITE_TAG not in tools[n]}


async def test_status_is_served_under_every_selection():
    for selection in (
        Selection(toolsets=("wiki",)),
        Selection(toolsets=(CORE,), read_only=True),
        Selection(toolsets=("forms",), exclude_tools=("forms_surveys_get",)),
    ):
        assert {*ALWAYS_SERVED} <= await served(selection)


@pytest.mark.parametrize(
    "selection",
    [
        Selection(tools=("tracker_issues_gett", "wiki_pages_get")),
        Selection(exclude_tools=("tracker_issues_gett", "wiki_pages_get")),
    ],
)
async def test_an_unknown_tool_name_fails_loudly(selection):
    """FastMCP would silently match nothing; the server names the typo instead."""
    with pytest.raises(UnknownToolError, match="tracker_issues_gett"):
        await check_tool_names(selection)


@pytest.mark.parametrize(
    "selection",
    [
        Selection(),
        Selection(toolsets=("wiki",), tools=("tracker_issues_get",)),
        Selection(exclude_tools=("tracker_queues_delete",)),
        Selection(toolsets=(CORE, "wiki"), exclude_tools=("wiki_pages_delete",)),
        Selection(read_only=True),
        Selection(tool_search=True),
        Selection(toolsets=("tracker",), tools=("wiki_pages_get",), read_only=True),
    ],
)
async def test_a_client_connects_and_sees_what_a_direct_listing_shows(selection):
    """Connecting runs FastMCP's startup, which a direct ``server.list_tools()`` skips.

    That startup runs the server's transforms over the task-capable components only (none
    here): a name check placed among the transforms refused every ``--tools`` /
    ``--exclude-tools`` name there and closed the connection.
    """
    await check_tool_names(selection)
    async with Client(build_server(selection)) as client:
        names = {tool.name for tool in await client.list_tools()}
    assert names == await served(selection)


async def test_the_name_check_does_not_trip_on_good_names():
    selection = Selection(tools=("wiki_pages_get",), exclude_tools=("forms_surveys_get",))
    assert "forms_surveys_get" not in await served(selection)


async def test_a_name_from_an_unselected_service_is_checked_not_rejected():
    selection = Selection(toolsets=("wiki",), exclude_tools=("forms_surveys_get",))
    assert not {n for n in await served(selection) if n.startswith("forms_")}


async def test_tool_search_lists_a_search_interface_and_status():
    server = build_server(Selection(tool_search=True))
    async with Client(server) as client:
        names = {tool.name for tool in await client.list_tools()}
        assert names == {"search_tools", "call_tool", *ALWAYS_SERVED}
        found = await client.call_tool("search_tools", {"query": "tracker issue comments add"})
    assert "tracker_comments_create" in {
        item["name"] for item in found.structured_content["result"]
    }


async def test_tool_search_respects_the_selection(api):
    """Search finds only the selected tools, and the call proxy refuses the rest."""
    server = build_server(Selection(toolsets=(CORE,), read_only=True, tool_search=True))
    async with Client(server) as client:
        found = await client.call_tool("search_tools", {"query": "create issue comment"})
        hits = {item["name"] for item in found.structured_content["result"]}
        assert hits
        assert not hits & {"tracker_issues_create", "tracker_comments_create"}
        assert hits <= CORE_TOOLS
        with pytest.raises(ToolError, match="Unknown tool"):
            await client.call_tool("call_tool", {"name": "tracker_issues_create"})
        api.add("GET", f"{TRACKER_BASE}/issues/QA-1", json={"key": "QA-1"})
        result = await client.call_tool(
            "call_tool", {"name": "tracker_issues_get", "arguments": {"issue_key": "QA-1"}}
        )
    assert result.structured_content == {"key": "QA-1"} or "QA-1" in str(result.content)
