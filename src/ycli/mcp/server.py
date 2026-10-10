"""Root Yandex 360 FastMCP server: :func:`build_server` mounts the selected services.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per registered service (``tracker_*``, ``wiki_*``, ``forms_*``). Reads
and writes; the :class:`~ycli.mcp.selection.Selection` narrows what is served.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Annotated, Any

from fastmcp import Context  # noqa: TC002  # read at run time: FastMCP resolves the proxy's hints
from fastmcp.exceptions import ToolError
from fastmcp.server.transforms.search import BM25SearchTransform
from fastmcp.tools import Tool
from fastmcp.tools.base import ToolResult  # noqa: TC002  # the same
from pydantic import ValidationError

from ycli.mcp.listing import (
    DerivedTags,
    GrantsSaid,
    LightListing,
    ServedWithTheirTools,
    UnknownToolError,
)
from ycli.mcp.profiles import ALWAYS_SERVED
from ycli.mcp.schemas import schema_server
from ycli.mcp.selection import Selection
from ycli.settings import (
    OAUTH_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    AppConfig,
    MCPHTTPConfig,
    OAuthAppConfig,
)
from ycli.yandex.mcp import GRANTS_ACCESS, WRITE_TAG, guide, new_server
from ycli.yandex.registry import SERVICES, about
from ycli.yandex.status.mcp import mcp as status_mcp

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fastmcp import FastMCP
    from fastmcp.server.auth import AuthProvider

    from ycli.yandex.service import Service


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
        >>> server.name
        'yandex'
    """
    mounted_names = selection.services()
    mounted = [service for service in SERVICES if service.name in mounted_names]
    server = new_server("yandex", instructions=_instructions(mounted), auth=auth)

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
    # No tools for `ycli sync`: it works in the caller's working tree, and a server has none.
    server.mount(status_mcp, namespace="status")
    server.mount(schema_server(server.list_tools, server.get_tool), namespace="schema")
    server.add_transform(DerivedTags())
    server.add_transform(GrantsSaid())
    _apply_selection(server, selection)
    return server


#: What the proxy of the tool search answers when asked to run a tool that grants access.
BY_ITS_OWN_NAME = (
    "this tool grants access: call it by its own name, so that the client can ask a person"
)


def _grants_access(tool: Tool) -> bool:
    """Whether ``tool`` carries the mark of an operation that grants access."""
    return all((tool.meta or {}).get(key) is value for key, value in GRANTS_ACCESS.items())


class _Search(BM25SearchTransform):
    """The tool search, with the tools that grants access left in the listing.

    A client reads the mark of such a tool from the tool's own entry and asks a person. Behind
    the search there is no entry, and the proxy that runs what the search found carries no
    mark: nobody would be asked. So a marked tool stays listed, the search does not offer it,
    and the proxy refuses to run it. Which tools those are is read from their mark.

    It overrides two private methods of FastMCP's transform and takes the function of its
    proxy (written against FastMCP 4.0.11): the test through a real client
    (``test_mcp_selection``) is what holds the behaviour when FastMCP changes them.
    """

    async def transform_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        """The pinned tools, the marked ones, and the search and its proxy."""
        listed = await super().transform_tools(tools)
        there = {tool.name for tool in listed}
        marked = [tool for tool in tools if _grants_access(tool) and tool.name not in there]
        return [*marked, *listed]

    async def _get_visible_tools(self, ctx: Context) -> Sequence[Tool]:
        """What the search looks through: nothing the proxy would refuse."""
        found = await super()._get_visible_tools(ctx)
        return [tool for tool in found if not _grants_access(tool)]

    def _make_call_tool(self) -> Tool:
        """The proxy of FastMCP, which first looks at the mark of what it is asked to run."""
        proxy = super()._make_call_tool()
        run = proxy.fn  # ty: ignore[unresolved-attribute]

        async def call_tool(
            name: Annotated[str, "The name of the tool to call"],
            arguments: Annotated[dict[str, Any] | None, "Arguments to pass to the tool"] = None,
            ctx: Context = None,  # ty: ignore[invalid-parameter-default]
        ) -> ToolResult:
            tool = await ctx.fastmcp.get_tool(name)
            if tool is not None and _grants_access(tool):
                raise ToolError(BY_ITS_OWN_NAME)
            return await run(name, arguments, ctx)

        call_tool.__doc__ = run.__doc__
        return Tool.from_function(fn=call_tool, name=proxy.name)


def _instructions(mounted: list[Service]) -> str:
    """What the server tells a client about itself, from the registry: no service is written here.

    For each mounted service: what it is, how many resources it has, and the tool to begin
    with. A client may cut the text at 2 048 characters (Claude Code does), so what a caller
    needs first comes first; ``tests/architecture/test_tool_metadata.py`` holds the length.
    """
    services = " ".join(
        f"{service.name}_* — {about(service)}; start with {service.start}." for service in mounted
    )
    guides = ", ".join(f"ycli://{service.name}/guide" for service in mounted)
    return (
        f"Read/write access to Yandex 360. Tools are namespaced per service. {services} "
        f"Read the guide of a service before its first call, as a resource: {guides}. "
        "Every tool carries honest annotations: reads have readOnlyHint=true; writes "
        "have readOnlyHint=false and an explicit destructiveHint — treat destructiveHint=true "
        f"tools (delete/clear/abort) with care. Credentials come from the {OAUTH_TOKEN_ENV} "
        f"and {ORGANIZATION_ID_ENV} environment variables (over HTTP: the signed-in "
        "caller's Yandex account). "
        "Objects as files in git (pull, diff, push) are the CLI's: run `ycli sync --help`."
    )


def _apply_selection(server: FastMCP, selection: Selection) -> None:
    """Show only what ``selection`` serves. The order of the transforms matters: see each."""
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
        server.add_transform(_Search(always_visible=[*ALWAYS_SERVED]))
    server.add_transform(LightListing())  # last, so it slims the search tools and their results too


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
    requested = {*selection.tools, *selection.exclude_tools} - {*ALWAYS_SERVED}
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
