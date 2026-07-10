"""TDD for forms answers MCP subserver — only answers_list is exposed (get was removed)."""

from fastmcp import Client

from ycli.yandex.forms.answers import mcp as answers_mcp


async def test_answers_tools_registered_read_only():
    async with Client(answers_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "answers_list" in tools
    # The single-answer endpoint is not deployed (404 at every path); the tool was removed.
    assert "answers_get" not in tools
    assert tools["answers_list"].annotations.readOnlyHint is True
