"""The recovery subserver is intentionally tool-less (restore is a WRITE — ARCH-3).

It exists only for four-surface symmetry (ARCH-1); it must instantiate, connect, and expose
zero tools. Mounting it into a parent server therefore adds nothing (verified here too, so the
orchestrator can mount it for symmetry without changing the tool inventory).
"""

from fastmcp import Client, FastMCP

from ycli.yandex.wiki.recovery import mcp as recovery_mcp


async def test_recovery_subserver_registers_no_tools():
    async with Client(recovery_mcp.mcp) as client:
        tools = await client.list_tools()
    assert tools == []


async def test_recovery_subserver_mounts_cleanly_without_adding_tools():
    parent = FastMCP("parent")
    parent.mount(recovery_mcp.mcp)
    async with Client(parent) as client:
        tools = await client.list_tools()
    assert tools == []  # tool-less mount is a no-op — safe to include for symmetry
