"""``Service`` — how one Yandex service plugs into every surface (see ``registry.SERVICES``)."""

from __future__ import annotations

from dataclasses import dataclass
from pkgutil import resolve_name
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typer
    from fastmcp import FastMCP

    from ycli.yandex.base import DomainClient


@dataclass(frozen=True, slots=True)
class Service:
    """One Yandex service as every surface sees it.

    ``name`` is the CLI group, the MCP tool prefix (``tracker_*``) and the ``auth status`` key.
    """

    name: str
    help: str
    client: str
    cli: str
    mcp: str

    def client_class(self) -> type[DomainClient]:
        """The SDK client class (``TrackerClient``), imported on first use."""
        return resolve_name(self.client)

    def cli_app(self) -> typer.Typer:
        """The Typer sub-app mounted as ``ycli <name>``."""
        return resolve_name(self.cli)

    def mcp_server(self) -> FastMCP:
        """The FastMCP sub-server mounted under the ``<name>`` namespace (needs the extra)."""
        return resolve_name(self.mcp)
