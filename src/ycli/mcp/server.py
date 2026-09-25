"""Root Yandex 360 FastMCP server — mounts the per-domain subservers.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per domain: ``wiki_*``, ``tracker_*``, ``forms_*``. Reads and
writes; ``--read-only`` serves the reads-only view.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.server import default_lifespan

from ycli.log import configure
from ycli.settings import AppConfig, RequestAuthConfig
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.mcp import (
    WRITE_TAG,
    RequestAuth,
    YandexBearerVerifier,
    close_userinfo_client,
    set_request_auth,
    start_userinfo_client,
)
from ycli.yandex.status.mcp import mcp as status_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp

mcp = FastMCP(
    "yandex",
    instructions=(
        "Read/write access to Yandex 360: Tracker (issues, comments, worklog, …), "
        "Wiki (pages, grids, attachments), and Forms (surveys, questions, answers). "
        "Tools are namespaced wiki_*, tracker_*, forms_*. Every tool carries honest "
        "annotations: reads have readOnlyHint=true; writes have readOnlyHint=false and "
        "an explicit destructiveHint — treat destructiveHint=true tools (delete/clear/"
        "abort) with care. Credentials come from YANDEX_ID_* OAuth variables or "
        "YANDEX_CLOUD_* IAM variables."
    ),
)
mcp.mount(wiki_mcp, namespace="wiki")
mcp.mount(tracker_mcp, namespace="tracker")
mcp.mount(forms_mcp, namespace="forms")
mcp.mount(status_mcp, namespace="status")


@asynccontextmanager
async def http_userinfo_lifespan(server: FastMCP) -> AsyncIterator[dict[str, object]]:
    """Own the pooled Identity Hub client for exactly one HTTP server lifespan."""
    await start_userinfo_client()
    try:
        yield {}
    finally:
        await close_userinfo_client()


def configure_http_auth(verifier: YandexBearerVerifier | None = None) -> None:
    """Resolve fixed HTTP configuration once and protect the MCP endpoint."""
    config = RequestAuthConfig()  # ty: ignore[missing-argument]
    mcp.auth = verifier or YandexBearerVerifier()
    mcp._lifespan = http_userinfo_lifespan
    set_request_auth(RequestAuth(config.cloud_organization_id))


def main(
    read_only: bool = False,
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Run the root server over stdio or Streamable HTTP."""
    configure(
        level=AppConfig().log_level
    )  # match the CLI: single stderr sink, stdout stays clean for the protocol
    if read_only:
        mcp.disable(tags={WRITE_TAG})
    if transport == "streamable-http":
        configure_http_auth()
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.auth = None
        mcp._lifespan = default_lifespan
        set_request_auth(None)
        mcp.run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
