"""Wiki /upload_sessions FastMCP subserver — read-only (the ``get`` surface only).

The upload pipeline itself (create / upload-part / finish / abort) is a sequence of WRITES and
lives on the CLI + SDK (ARCH-3); the sole read — inspect a session's state — is exposed here so
an agent can poll a session's ``status`` while a human or the CLI drives the upload.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, TAGS, wiki_client
from ycli.yandex.wiki.uploadsessions.models import UploadSession

mcp = FastMCP("wiki-uploadsessions")


@mcp.tool(
    name="uploadsessions_get",
    annotations={**RO, "title": "Get Wiki upload session"},
    tags=TAGS,
)
def get(
    session_id: Annotated[str, Field(description="UUID4 of the upload session to inspect.")],
    client: WikiClient = Depends(wiki_client),
) -> UploadSession:
    """Current state of a Wiki file upload session by its UUID (status, file name/size, storage).

    Poll this to watch a session move ``not_started`` → ``in_progress`` → ``finished`` before the
    file is attached to a page. The pipeline writes (create / upload-part / finish / abort) are
    CLI/SDK only — this is the session resource's sole read surface.

    Example:
        >>> get(session_id="1e5c4b2a-…")  # doctest: +SKIP
    """
    return client.uploadsessions.get(session_id=session_id)
