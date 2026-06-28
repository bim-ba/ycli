"""Root MCP server: the 3 subservers mount with namespaced tool names."""

import pytest
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


@pytest.mark.integration
def test_mcp_main_honors_log_level(monkeypatch, capsys):
    monkeypatch.setenv("YCLI_LOG_LEVEL", "ERROR")
    import ycli.mcp as mcp_module
    monkeypatch.setattr(mcp_module.mcp, "run", lambda *a, **k: None)
    from ycli.mcp import main
    from loguru import logger
    main()
    logger.info("hidden_line")
    logger.error("shown_line")
    err = capsys.readouterr().err
    assert "hidden_line" not in err
    assert "shown_line" in err
