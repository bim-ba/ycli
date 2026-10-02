"""Root Yandex 360 FastMCP server: :func:`build_server` mounts the selected services.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per registered service (``tracker_*``, ``wiki_*``, ``forms_*``). Reads
and writes; the :class:`~ycli.mcp.selection.Selection` narrows what is served.
"""

from __future__ import annotations

import asyncio

from fastmcp import FastMCP
from fastmcp.server.transforms.search import BM25SearchTransform

from ycli.mcp.listing import KnownTools, LightListing
from ycli.mcp.profiles import STATUS_TOOL
from ycli.mcp.selection import Selection
from ycli.settings import OAUTH_TOKEN_ENV, ORGANIZATION_ID_ENV
from ycli.yandex.mcp import WRITE_TAG
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.mcp import mcp as status_mcp


def build_server(selection: Selection) -> FastMCP:
    """The root server for ``selection``: only the selected services are imported and mounted.

    The server does not check tool names until it lists tools (:func:`main` does so before
    serving): an unknown name in ``tools`` / ``exclude_tools`` raises ``UnknownToolError``.

    Example:
        >>> server = build_server(Selection(toolsets=("wiki",)))
        >>> isinstance(server, FastMCP)
        True
    """
    mounted_names = selection.services()
    mounted = [service for service in SERVICES if service.name in mounted_names]
    server = FastMCP(
        "yandex",
        instructions=(
            "Read/write access to Yandex 360. Tools are namespaced per service: "
            + "; ".join(f"{service.name}_* — {service.help}" for service in mounted)
            + ". Every tool carries honest annotations: reads have readOnlyHint=true; writes "
            "have readOnlyHint=false and an explicit destructiveHint — treat destructiveHint=true "
            f"tools (delete/clear/abort) with care. Credentials come from the {OAUTH_TOKEN_ENV} "
            f"and {ORGANIZATION_ID_ENV} environment variables."
        ),
    )
    for service in mounted:
        server.mount(service.mcp_server(), namespace=service.name)
    server.mount(status_mcp, namespace="status")

    server.add_transform(KnownTools(frozenset({*selection.tools, *selection.exclude_tools})))
    if not selection.serves_everything:
        server.enable(names=set(selection.listed_names()), only=True)
        for name in selection.listed_services():
            server.enable(tags={name})
    if selection.exclude_tools:
        server.disable(names=set(selection.exclude_tools))
    if selection.read_only:
        server.disable(tags={WRITE_TAG})
    if selection.tool_search:
        server.add_transform(BM25SearchTransform(always_visible=[STATUS_TOOL]))
    server.add_transform(LightListing())  # last, so it slims the search tools and their results too
    return server


def main(selection: Selection) -> None:
    """Run the root server for ``selection`` over stdio (the console-script entry point).

    Example:
        >>> main(Selection())  # doctest: +SKIP
    """
    server = build_server(selection)
    asyncio.run(server.list_tools())  # fail on an unknown tool name before serving, not later
    server.run()


if __name__ == "__main__":  # pragma: no cover
    main(Selection())
