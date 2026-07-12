"""Root MCP server: the 3 subservers mount with namespaced tool names."""

import pytest
from fastmcp import Client

from ycli.mcp import mcp


def test_base_install_imports_cli_without_fastmcp():
    """`ycli.mcp.cli` (and `ycli.cli`) must import without pulling fastmcp — base install."""
    import subprocess
    import sys

    code = "import ycli.cli, ycli.mcp.cli, sys; assert 'fastmcp' not in sys.modules"
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


async def test_root_mounts_all_domains_with_namespaces():
    async with Client(mcp) as client:
        names = {t.name for t in await client.list_tools()}
    # Membership smoke-check that each domain mounted under its namespace. The exact tool
    # surface (all 81 names) is pinned authoritatively by tests/snapshots/mcp_tools.txt via
    # test_snapshots.py — kept there as the single source of truth, not duplicated as counts here.
    assert "wiki_pages_get" in names
    assert "tracker_issues_get" in names
    assert "forms_surveys_get" in names
    assert "status_get" in names


def test_main_is_callable():
    from ycli.mcp import main

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


def test_main_read_only_disables_write_tag(monkeypatch):
    """main(read_only=True) hides the write tag before serving; default leaves it visible."""
    from ycli.mcp import server
    from ycli.yandex.mcp import WRITE_TAG

    recorded: dict[str, object] = {}
    monkeypatch.setattr(server.mcp, "run", lambda *a, **k: recorded.setdefault("ran", True))
    monkeypatch.setattr(
        server.mcp, "disable", lambda **kwargs: recorded.setdefault("disabled", kwargs)
    )
    server.main(read_only=True)
    assert recorded == {"disabled": {"tags": {WRITE_TAG}}, "ran": True}

    recorded.clear()
    server.main()
    assert recorded == {"ran": True}


def test_mcp_main_module_importable():
    """``python -m ycli.mcp`` entry resolves — covers the __main__.py import line."""
    import ycli.mcp.__main__  # noqa: F401


@pytest.mark.integration
def test_mcp_main_honors_log_level(monkeypatch, capsys):
    monkeypatch.setenv("YCLI_LOG_LEVEL", "ERROR")
    import ycli.mcp as mcp_module

    monkeypatch.setattr(mcp_module.mcp, "run", lambda *a, **k: None)
    from loguru import logger

    from ycli.mcp import main

    main()
    logger.info("hidden_line")
    logger.error("shown_line")
    err = capsys.readouterr().err
    assert "hidden_line" not in err
    assert "shown_line" in err
