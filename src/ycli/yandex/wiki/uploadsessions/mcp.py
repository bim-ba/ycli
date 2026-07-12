"""Wiki /upload_sessions FastMCP tools — the full upload pipeline plus the ``get`` read.

The pipeline: ``uploadsessions_create`` opens a session, ``uploadsessions_upload_part``
PUTs the file bytes (base64 in the request, raw octet-stream on the wire),
``uploadsessions_finish`` closes it, then ``attachments_attach`` wires the finished session
to a page (``attachments_upload`` runs all four steps for one small file).
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Base64Bytes, Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import DESTRUCTIVE, RO, TAGS, WRITE, WRITE_TAGS, wiki_client
from ycli.yandex.wiki.uploadsessions.models import (
    AbortActiveUploadsResult,
    UploadSession,
    UploadSessionCreate,
)

mcp = FastMCP("wiki-uploadsessions")

SessionIdParam = Annotated[str, Field(description="UUID4 of the upload session.")]


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
    file is attached to a page.

    Example:
        >>> get(session_id="1e5c4b2a-…")  # doctest: +SKIP
    """
    return client.uploadsessions.get(session_id=session_id)


@mcp.tool(
    name="uploadsessions_create",
    annotations={**WRITE, "title": "Create Wiki upload session"},
    tags=WRITE_TAGS,
)
def create(
    body: Annotated[
        UploadSessionCreate,
        Field(description="``file_name`` + total ``file_size`` in bytes (sum of every part)."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> UploadSession:
    """Open an upload session — step 1 of the Wiki file-upload pipeline.

    The returned ``session_id`` addresses the session for ``uploadsessions_upload_part`` /
    ``uploadsessions_finish``. For a single small file, ``attachments_upload`` runs the whole
    pipeline in one call instead.

    Example:
        >>> create(body={"file_name": "d.png", "file_size": 2048})  # doctest: +SKIP
    """
    return client.uploadsessions.create(body)


@mcp.tool(
    name="uploadsessions_upload_part",
    annotations={**WRITE, "title": "Upload Wiki file part"},
    tags=WRITE_TAGS,
)
def upload_part(
    session_id: SessionIdParam,
    part_number: Annotated[
        int, Field(description="1-based part index (1 for the first part, +1 for each next).")
    ],
    data: Annotated[Base64Bytes, Field(description="This part's bytes, base64-encoded.")],
    client: WikiClient = Depends(wiki_client),
) -> UploadSession:
    """Upload one file part to an open session — step 2 of the upload pipeline.

    The base64 ``data`` is decoded and sent as raw ``application/octet-stream`` bytes.
    Parts may be 5-16 MB except the last; a small file fits in a single ``part_number=1``
    call. Returns the session (poll ``status`` via ``uploadsessions_get``).

    Example:
        >>> upload_part(session_id="1e5c…", part_number=1, data="aGk=")  # doctest: +SKIP
    """
    return client.uploadsessions.upload_part(session_id, part_number=part_number, data=data)


@mcp.tool(
    name="uploadsessions_finish",
    annotations={**WRITE, "title": "Finish Wiki upload session"},
    tags=WRITE_TAGS,
)
def finish(
    session_id: SessionIdParam,
    client: WikiClient = Depends(wiki_client),
) -> UploadSession:
    """Close an upload session after its last part — step 3 of the upload pipeline.

    Only a finished session can be attached to a page (``attachments_attach``). Returns the
    session with its final ``status``.

    Example:
        >>> finish(session_id="1e5c…")  # doctest: +SKIP
    """
    return client.uploadsessions.finish(session_id=session_id)


@mcp.tool(
    name="uploadsessions_abort",
    annotations={**DESTRUCTIVE, "title": "Abort Wiki upload session"},
    tags=WRITE_TAGS,
)
def abort(
    session_id: SessionIdParam,
    client: WikiClient = Depends(wiki_client),
) -> UploadSession:
    """Cancel one in-progress upload session, discarding its uploaded parts.

    Frees the session's quota; the session cannot be resumed afterwards. Returns the
    session with ``status: aborted``.

    Example:
        >>> abort(session_id="1e5c…")  # doctest: +SKIP
    """
    return client.uploadsessions.abort(session_id=session_id)


@mcp.tool(
    name="uploadsessions_abort_all",
    annotations={**DESTRUCTIVE, "title": "Abort all Wiki upload sessions"},
    tags=WRITE_TAGS,
)
def abort_all(
    client: WikiClient = Depends(wiki_client),
) -> AbortActiveUploadsResult:
    """Cancel EVERY active upload session of the caller, discarding all uploaded parts.

    A quota-freeing sweep — use it when stale sessions block new uploads; prefer
    ``uploadsessions_abort`` to cancel a single known session.

    Example:
        >>> abort_all()  # doctest: +SKIP
    """
    return client.uploadsessions.abort_all()
