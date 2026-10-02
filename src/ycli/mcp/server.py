"""Root Yandex 360 FastMCP server: :func:`build_server` mounts the selected services.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per registered service (``tracker_*``, ``wiki_*``, ``forms_*``). Reads
and writes; the :class:`~ycli.mcp.selection.Selection` narrows what is served.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from fastmcp import FastMCP
from fastmcp.server.transforms.search import BM25SearchTransform
from pydantic import ValidationError

from ycli.mcp.listing import KnownTools, LightListing
from ycli.mcp.profiles import STATUS_TOOL
from ycli.mcp.selection import Selection
from ycli.settings import (
    OAUTH_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    AppConfig,
    MCPHTTPConfig,
    OAuthAppConfig,
)
from ycli.yandex.mcp import WRITE_TAG
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.mcp import mcp as status_mcp

if TYPE_CHECKING:
    from fastmcp.server.auth import AuthProvider


def build_server(selection: Selection, auth: AuthProvider | None = None) -> FastMCP:
    """The root server for ``selection``: only the selected services are imported and mounted.

    ``auth`` signs callers in (HTTP only, see :func:`serve_http`); over stdio there is none and
    the tools use the environment's credentials.

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
            f"and {ORGANIZATION_ID_ENV} environment variables (over HTTP: the signed-in "
            "caller's Yandex account)."
        ),
        auth=auth,
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


def _settings_problems(exc: ValidationError) -> str:
    """``exc`` as ``VARIABLE: problem`` pairs, named as the environment spells them.

    Example:
        >>> try:
        ...     MCPHTTPConfig(organization_id="1", base_url="nope")
        ... except ValidationError as exc:
        ...     _settings_problems(exc)
        'YCLI__MCP__BASE_URL: Input should be a valid URL, relative URL without a base'
    """
    names = {"organization_id": ORGANIZATION_ID_ENV}
    return "; ".join(
        f"{names.get(field, f'YCLI__MCP__{field.upper()}')}: {error['msg']}"
        for error in exc.errors()
        if (field := str(error["loc"][0]) if error["loc"] else "")
    )


def serve_http(selection: Selection, host: str | None = None, port: int | None = None) -> None:
    """Serve ``selection`` over Streamable HTTP, every caller signed in through Yandex ID.

    Reads ``YCLI__MCP__*`` (:class:`~ycli.settings.MCPHTTPConfig`) and the Yandex OAuth app
    (``YANDEX_OAUTH_CLIENT_ID`` / ``YANDEX_OAUTH_CLIENT_SECRET``); ``host`` / ``port`` override
    the configured ones. Requests are stateless; the OAuth state lives in ``FASTMCP_HOME``,
    so one process serves (docs/self-host.md).

    Example:
        >>> serve_http(Selection(toolsets=("core",)), port=8080)  # doctest: +SKIP
    """
    from ycli.mcp.http_auth import yandex_oauth

    try:
        config = MCPHTTPConfig()  # ty: ignore[missing-argument]  # pydantic-settings reads the env
    except ValidationError as exc:
        raise ValueError(f"MCP over HTTP is not configured: {_settings_problems(exc)}") from exc
    app = OAuthAppConfig()
    if not app.client_id or app.client_secret is None:
        raise ValueError(
            "MCP over HTTP signs callers in with your Yandex OAuth app: set "
            "YANDEX_OAUTH_CLIENT_ID and YANDEX_OAUTH_CLIENT_SECRET"
        )
    auth = yandex_oauth(config, app.client_id, app.client_secret, AppConfig().http)
    server = build_server(selection, auth=auth)
    asyncio.run(server.list_tools())  # fail on an unknown tool name before serving, not later
    server.run(
        transport="http", host=host or config.host, port=port or config.port, stateless_http=True
    )


if __name__ == "__main__":  # pragma: no cover
    main(Selection())
