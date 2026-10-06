"""Root MCP server: the 3 subservers mount with namespaced tool names."""

import pytest
from fastmcp import Client

from tests.full_server import mcp


def test_base_install_imports_cli_without_fastmcp():
    """`ycli.mcp.cli` (and `ycli.cli`) must import without pulling fastmcp — base install."""
    import subprocess
    import sys

    code = "import ycli.cli, ycli.mcp.cli, sys; assert 'fastmcp' not in sys.modules"
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


MCP_ONLY = """
import asyncio, httpx2
from fastmcp import Client
from tests.contract import load_cases
from tests.full_server import mcp

case = next(case for case in load_cases() if case.operation == "forms.questions.list")
reply = case.exchanges[0][1]
transport = httpx2.MockTransport(lambda request: httpx2.Response(reply.status, json=reply.json))
import ycli.yandex.core.session as session
session.default_transport = lambda: transport

async def call():
    async with Client(mcp) as client:
        return (await client.call_tool(*case.mcp)).structured_content

print(asyncio.run(call()))
"""


def test_a_tool_answers_when_nothing_has_used_its_models_before():
    """A server process calls a tool with no SDK call before it: the listing of questions answers.

    In an interpreter of its own, since the contract test calls the SDK first in the same
    process, and that alone finishes a model pydantic left incomplete (v0.46.0 to v0.94.0).
    """
    import subprocess
    import sys
    from pathlib import Path

    proc = subprocess.run(
        [sys.executable, "-c", MCP_ONLY],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[3],
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert "'slug': 'name'" in proc.stdout


async def test_root_mounts_all_domains_with_namespaces():
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
    # Membership smoke-check that each domain mounted under its namespace. The exact tool
    # surface (all 81 names) is pinned authoritatively by tests/snapshots/mcp_signatures.txt via
    # test_snapshots.py — kept there as the single source of truth, not duplicated as counts here.
    assert "wiki_pages_get" in names
    assert "tracker_issues_get" in names
    assert "forms_surveys_get" in names
    assert "status_get" in names


def test_main_is_callable():
    from ycli.mcp.server import main

    assert callable(main)


async def test_disable_write_tag_hides_mounted_write_tools():
    """root.disable(tags={WRITE_TAG}) hides write-tagged tools mounted from subservers."""
    from fastmcp import FastMCP

    from ycli.yandex.mcp import RO, WRITE, WRITE_TAG

    sub = FastMCP("sub")

    @sub.tool(name="things_list", annotations={**RO, "title": "List things"}, tags={"sub"})
    def things_list() -> str:
        """List things."""
        return "things"

    @sub.tool(
        name="things_create",
        annotations={**WRITE, "title": "Create a thing"},
        tags={"sub", WRITE_TAG},
    )
    def things_create() -> str:
        """Create a thing."""
        return "thing"

    root = FastMCP("root")
    root.mount(sub, namespace="sub")
    root.disable(tags={WRITE_TAG})
    async with Client(root) as client:
        names = {t.name for t in await client.list_tools()}
    assert "sub_things_list" in names
    assert "sub_things_create" not in names


def test_main_validates_then_serves(monkeypatch):
    """main() lists tools first (so a bad name fails before serving), then runs the server."""
    from fastmcp import FastMCP

    from ycli.mcp.listing import UnknownToolError
    from ycli.mcp.selection import Selection
    from ycli.mcp.server import main

    ran: list[bool] = []
    monkeypatch.setattr(FastMCP, "run", lambda self, *args, **kwargs: ran.append(True))
    main(Selection(toolsets=("wiki",)))
    assert ran == [True]

    with pytest.raises(UnknownToolError, match="tracker_issues_gett"):
        main(Selection(tools=("tracker_issues_gett",)))
    assert ran == [True]  # the bad selection never reached run()


def test_mcp_main_module_importable():
    """``python -m ycli.mcp`` entry resolves — covers the __main__.py import line."""
    import ycli.mcp.__main__  # noqa: F401
