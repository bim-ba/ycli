"""``Service`` — how one Yandex service plugs into every surface (see ``registry.SERVICES``)."""

from __future__ import annotations

from dataclasses import dataclass
from pkgutil import resolve_name
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from ycli.yandex.base import DomainClient
    from ycli.yandex.core.pagination import Pagination
    from ycli.yandex.core.profile import ServiceProfile


@dataclass(frozen=True, slots=True)
class Service:
    """One Yandex service as every surface sees it.

    ``name`` is the CLI group, the MCP tool prefix (``tracker_*``) and the ``auth status`` key;
    ``profile`` is where its API lives and how it names the organization. ``pagination`` names
    (like ``client``) the one :class:`~ycli.yandex.core.pagination.Pagination` that every listing
    of the service shares, or is ``None`` when its listings page in more than one way.
    """

    name: str
    help: str
    client: str
    cli: str
    mcp: str
    profile: ServiceProfile
    pagination: str | None = None

    def client_class(self) -> type[DomainClient]:
        """The SDK client class (``TrackerClient``), imported on first use."""
        return resolve_name(self.client)

    def listing_pagination(self) -> Pagination | None:
        """How every listing of the service pages (``ycli api --paginate``), if one way fits all."""
        return None if self.pagination is None else resolve_name(self.pagination)

    def mcp_server(self) -> FastMCP:
        """The FastMCP sub-server mounted under the ``<name>`` namespace (needs the extra)."""
        return resolve_name(self.mcp)
