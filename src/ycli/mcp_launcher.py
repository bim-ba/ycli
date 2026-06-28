"""The ``ycli mcp`` launcher — isolated so cli.py only mounts. Importable without the mcp extra."""
from __future__ import annotations

import typer


def launch_mcp_server() -> None:
    """Run the read-only MCP server over stdio (requires the ``mcp`` extra).

    Tools are namespaced ``wiki_*``, ``tracker_*``, ``forms_*``. Point an MCP client at
    ``ycli mcp``.
    """
    try:
        from ycli.mcp import main as run_server
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the 'mcp' extra
        raise typer.BadParameter(
            "The MCP server requires the 'mcp' extra. Install it with: "
            "uv add 'yandex-cli[mcp]'  (or: uv tool install 'yandex-cli[mcp]')."
        ) from exc
    run_server()
