"""``ycli mcp`` sub-app: run the server and list its tools. Importable without the mcp extra."""

from __future__ import annotations

from enum import StrEnum

import typer


class Transport(StrEnum):
    stdio = "stdio"
    streamable_http = "streamable-http"


app = typer.Typer(name="mcp", help="MCP server control (reads + writes).", no_args_is_help=True)

_MISSING = (
    "The MCP server requires the 'mcp' extra. Install it with: "
    "uv add 'yandex-cli[mcp]'  (or: uv tool install 'yandex-cli[mcp]')."
)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager import, --help stays extra-free)."""


@app.command()
def start(
    read_only: bool = typer.Option(
        False,
        "--read-only",
        help="Serve only read tools (hide every write-tagged tool).",
    ),
    transport: Transport = typer.Option(  # noqa: B008
        Transport.stdio,
        "--transport",
        help="MCP transport: stdio or streamable-http.",
    ),
    host: str = typer.Option("127.0.0.1", "--host", help="HTTP bind host."),
    port: int = typer.Option(8000, "--port", min=1, max=65535, help="HTTP bind port."),
) -> None:
    """Run the MCP server (tools namespaced wiki_*, tracker_*, forms_*)."""
    try:
        from ycli.mcp import main as run_server
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc
    run_server(read_only=read_only, transport=transport.value, host=host, port=port)


@app.command()
def methods() -> None:
    """List the MCP tool names exposed by the server."""
    import asyncio

    try:
        from fastmcp import Client

        from ycli.mcp import mcp
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc

    async def _list() -> None:
        async with Client(mcp) as client:
            for tool in sorted(t.name for t in await client.list_tools()):
                typer.echo(tool)

    asyncio.run(_list())
