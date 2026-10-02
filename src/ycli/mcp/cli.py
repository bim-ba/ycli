"""``ycli mcp`` sub-app: run the server and list its tools. Importable without the mcp extra."""

from __future__ import annotations

import typer

from ycli.yandex.registry import SERVICES

# Help text lives with the root sub-app list (ycli.cli.app).
app = typer.Typer(name="mcp", no_args_is_help=True)

_MISSING = (
    "The MCP server requires the 'mcp' extra. Install it with: "
    "uv add 'yandex-cli[mcp]'  (or: uv tool install 'yandex-cli[mcp]')."
)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager import, --help stays extra-free)."""


_NAMESPACES = ", ".join(f"{service.name}_*" for service in SERVICES)


@app.command(help=f"Run the MCP server over stdio (tools namespaced {_NAMESPACES}, status_*).")
def start(
    read_only: bool = typer.Option(
        False,
        "--read-only",
        help="Serve only read tools (hide every write-tagged tool).",
    ),
) -> None:
    try:
        from ycli.mcp.server import main as run_server
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc
    run_server(read_only=read_only)


@app.command()
def methods() -> str:
    """List the MCP tool names exposed by the server, one per line."""
    import asyncio

    try:
        from fastmcp import Client

        from ycli.mcp.server import mcp
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc

    async def _list() -> list[str]:
        async with Client(mcp) as client:
            return sorted(tool.name for tool in await client.list_tools())

    return "\n".join(asyncio.run(_list()))
