"""Root MCP server: the 3 subservers mount with namespaced tool names."""

from fastmcp import Client

from ycli.mcp import mcp


async def test_root_mounts_all_domains_with_namespaces():
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert "wiki_pages_get" in names
    assert "tracker_issues_get" in names
    assert "forms_surveys_get" in names
    assert len([n for n in names if n.startswith("wiki_")]) == 6
    assert len([n for n in names if n.startswith("tracker_")]) == 14
    assert len([n for n in names if n.startswith("forms_")]) == 5
    assert len(names) == 25


def test_main_is_callable():
    from ycli.mcp import main

    assert callable(main)
