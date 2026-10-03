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

from ycli.mcp.listing import LightListing, ServedWithTheirTools, UnknownToolError
from ycli.mcp.profiles import STATUS_TOOL
from ycli.mcp.selection import Selection
from ycli.settings import (
    OAUTH_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    AppConfig,
    MCPHTTPConfig,
    OAuthAppConfig,
)
from ycli.yandex.mcp import WRITE_TAG, guide
from ycli.yandex.registry import SERVICES
from ycli.yandex.status.mcp import mcp as status_mcp

if TYPE_CHECKING:
    from fastmcp.server.auth import AuthProvider


def build_server(selection: Selection, auth: AuthProvider | None = None) -> FastMCP:
    """The root server for ``selection``: only the selected services are imported and mounted.

    ``auth`` signs callers in (HTTP only, see :func:`serve_http`); over stdio there is none and
    the tools use the environment's credentials.

    The server does not check the names in ``tools`` / ``exclude_tools``: FastMCP silently
    matches nothing for an unknown one. :func:`check_tool_names` does, before serving.

    Args:
        selection: Which services and tools to serve, and how.
        auth: The sign-in provider for HTTP; ``None`` over stdio.

    Returns:
        The root server with the selected services mounted.

    Examples:
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
            "caller's Yandex account). Each service has a guide to read before its first call, "
            "as a resource: "
            + ", ".join(f"ycli://{service.name}/guide" for service in mounted)
            + "."
        ),
        auth=auth,
    )

    @server.resource(
        "ycli://guide",
        name="guide",
        title="How to work with Yandex 360 through ycli",
        mime_type="text/markdown",
    )
    def root_guide() -> str:
        """Where to start with Yandex 360 through ycli: access, and which service guide to read."""
        return guide("ycli.mcp")

    for service in mounted:
        server.mount(service.mcp_server(), namespace=service.name)
    server.mount(status_mcp, namespace="status")

    if not selection.serves_everything:
        server.enable(names=set(selection.listed_names()), only=True)
        for name in selection.listed_services():
            server.enable(tags={name})
    if selection.exclude_tools:
        server.disable(names=set(selection.exclude_tools))
    if selection.read_only:
        server.disable(tags={WRITE_TAG})
    # `enable(only=True)` above hides prompts and resources too: they follow their tools
    # instead (before the search transform, which replaces the tool listing).
    server.enable(components={"prompt", "resource", "template"})
    server.add_transform(ServedWithTheirTools(server.list_tools))
    if selection.tool_search:
        server.add_transform(BM25SearchTransform(always_visible=[STATUS_TOOL]))
    server.add_transform(LightListing())  # last, so it slims the search tools and their results too
    return server


async def check_tool_names(selection: Selection) -> None:
    """Fail when a name in ``tools`` / ``exclude_tools`` is no tool of its service.

    A typo would otherwise show or hide the wrong set without a word. It reads the services'
    own servers, not a listing of the root one: at startup FastMCP runs the root's transforms
    over the task-capable components only, so a check placed there refuses every name.

    Args:
        selection: Which services and tools to serve, and how.

    Raises:
        UnknownToolError: A requested name matches no tool.

    Examples:
        >>> asyncio.run(check_tool_names(Selection(tools=("wiki_pages_get",))))
    """
    requested = {*selection.tools, *selection.exclude_tools} - {STATUS_TOOL}
    if not requested:
        return
    mounted = selection.services()
    known = {
        f"{service.name}_{tool.name}"
        for service in SERVICES
        if service.name in mounted
        for tool in await service.mcp_server().list_tools()
    }
    if unknown := sorted(requested - known):
        raise UnknownToolError(f"unknown tool name(s): {', '.join(unknown)}")


def main(selection: Selection) -> None:
    """Run the root server for ``selection`` over stdio (the console-script entry point).

    Args:
        selection: Which services and tools to serve, and how.

    Examples:
        >>> main(Selection())  # doctest: +SKIP
    """
    asyncio.run(check_tool_names(selection))
    build_server(selection).run()


def _settings_problems(exc: ValidationError) -> str:
    """``exc`` as ``VARIABLE: problem`` pairs, named as the environment spells them.

    Args:
        exc: The validation error of the HTTP settings.

    Returns:
        The ``VARIABLE: problem`` pairs joined by ``; ``.

    Examples:
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
    so one process serves (docs/en/how-to/self-host-over-http.md).

    Args:
        selection: Which services and tools to serve, and how.
        host: Overrides the configured host.
        port: Overrides the configured port.

    Raises:
        ValueError: The HTTP settings or the Yandex OAuth app are not configured.

    Examples:
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
    asyncio.run(check_tool_names(selection))
    build_server(selection, auth=auth).run(
        transport="http", host=host or config.host, port=port or config.port, stateless_http=True
    )


if __name__ == "__main__":
    main(Selection())
