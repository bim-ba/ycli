"""``ycli mcp`` sub-app: run the server and list its tools. Importable without the mcp extra."""

from __future__ import annotations

import enum
from typing import Annotated

import typer

from ycli.cli.global_options import refuse_dry_run
from ycli.mcp.selection import ALL, TOOLSET_NAMES, Selection, split_names
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

_Toolsets = Annotated[
    str,
    typer.Option(
        "--toolsets",
        help=(
            f"Comma-separated toolsets to serve: {', '.join(TOOLSET_NAMES)} (core = a curated "
            "everyday profile; all = every service, the default). status_get is always served."
        ),
    ),
]
_Tools = Annotated[
    str,
    typer.Option("--tools", help="Comma-separated extra tool names to serve beyond the toolsets."),
]
_ExcludeTools = Annotated[
    str, typer.Option("--exclude-tools", help="Comma-separated tool names to hide.")
]
_ReadOnly = Annotated[
    bool,
    typer.Option(
        "--read-only",
        help="Serve only read tools (hide every write-tagged tool); wins over --tools.",
    ),
]
_ToolSearch = Annotated[
    bool,
    typer.Option(
        "--tool-search",
        help="List a search tool and a call proxy instead of the tools (BM25); status_get stays.",
    ),
]


class Transport(enum.StrEnum):
    """How MCP clients reach the server."""

    stdio = "stdio"
    http = "http"


_Transport = Annotated[
    Transport,
    typer.Option(
        "--transport",
        help=(
            "stdio (default): one local client, credentials from the environment. http: "
            "Streamable HTTP for many users, each signed in through Yandex ID (needs "
            "YCLI__MCP__BASE_URL and your Yandex OAuth app; see "
            "https://bim-ba.github.io/ycli/how-to/self-host-over-http/)."
        ),
    ),
]
_Host = Annotated[
    str | None, typer.Option("--host", help="HTTP only: listen address (YCLI__MCP__HOST).")
]
_Port = Annotated[
    int | None, typer.Option("--port", help="HTTP only: listen port (YCLI__MCP__PORT).")
]


def _selection(
    toolsets: str, tools: str, exclude_tools: str, read_only: bool, tool_search: bool
) -> Selection:
    """The flags as a :class:`Selection`; a bad name is a usage error, not a traceback."""
    try:
        return Selection(
            toolsets=split_names(toolsets),
            tools=split_names(tools),
            exclude_tools=split_names(exclude_tools),
            read_only=read_only,
            tool_search=tool_search,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command(help=f"Run the MCP server (tools namespaced {_NAMESPACES}, status_*).")
def start(
    toolsets: _Toolsets = ALL,
    tools: _Tools = "",
    exclude_tools: _ExcludeTools = "",
    read_only: _ReadOnly = False,
    tool_search: _ToolSearch = False,
    transport: _Transport = Transport.stdio,
    host: _Host = None,
    port: _Port = None,
    *,
    context: typer.Context,
) -> None:
    """Start the MCP server on the chosen transport."""
    refuse_dry_run(context, "mcp start serves tools and sends nothing itself; use --read-only.")
    selection = _selection(toolsets, tools, exclude_tools, read_only, tool_search)
    try:
        from ycli.mcp.listing import UnknownToolError
        from ycli.mcp.server import main as run_server
        from ycli.mcp.server import serve_http
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc
    try:
        if transport is Transport.http:
            serve_http(selection, host=host, port=port)
        else:
            run_server(selection)
    except UnknownToolError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except ValueError as exc:  # the HTTP transport is not configured
        raise typer.BadParameter(str(exc)) from exc


@app.command()
def methods(
    toolsets: _Toolsets = ALL,
    tools: _Tools = "",
    exclude_tools: _ExcludeTools = "",
    read_only: _ReadOnly = False,
    tool_search: _ToolSearch = False,
) -> str:
    """List the MCP tool names a server with the same flags exposes, one per line."""
    import asyncio

    selection = _selection(toolsets, tools, exclude_tools, read_only, tool_search)
    try:
        from ycli.mcp.listing import UnknownToolError
        from ycli.mcp.server import build_server
    except ModuleNotFoundError as exc:  # pragma: no cover - only without the extra
        raise typer.BadParameter(_MISSING) from exc

    async def _list() -> list[str]:
        return sorted(tool.name for tool in await build_server(selection).list_tools())

    try:
        return "\n".join(asyncio.run(_list()))
    except UnknownToolError as exc:
        raise typer.BadParameter(str(exc)) from exc
