"""The dashboards subserver is intentionally tool-less (create/add-widget are WRITEs — ARCH-3).

It exists only for four-surface symmetry (ARCH-1); it must instantiate, connect, and expose
zero tools, and mounting it into a parent adds nothing.
"""

from fastmcp import Client, FastMCP

from ycli.yandex.tracker.dashboards import mcp as dashboards_mcp


async def test_dashboards_subserver_registers_no_tools():
    async with Client(dashboards_mcp.mcp) as client:
        tools = await client.list_tools()
    assert tools == []


async def test_dashboards_subserver_mounts_cleanly_without_adding_tools():
    parent = FastMCP("parent")
    parent.mount(dashboards_mcp.mcp)
    async with Client(parent) as client:
        tools = await client.list_tools()
    assert tools == []  # tool-less mount is a no-op — safe to include for symmetry
