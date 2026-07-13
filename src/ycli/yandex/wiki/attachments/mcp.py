"""Wiki /pages/{id}/attachments FastMCP tools (list + attach/upload/delete writes).

Binary *downloads* stay CLI/SDK-only (base64 blobs are not an agent payload); the upload
direction is exposed — an agent supplies small file bytes as base64 in the request.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Base64Bytes, Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.wiki.attachments.models import AttachedFileList, AttachmentList
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    app_config,
    wiki_client,
)

mcp = FastMCP("wiki-attachments")


@mcp.tool(name="attachments_list", annotations={**RO, "title": "List Wiki attachments"}, tags=TAGS)
def list_(
    page_id: int,
    limit: int = 0,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> AttachmentList:
    """Attachments (name, size, mime type) on a page id, auto-paginated (drains ``next_cursor``).

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. This is the list surface;
    downloading an attachment's bytes is CLI/SDK-only (binary blobs are not an MCP payload).
    """
    cap = resolve_cap(limit, config.max_items)
    return client.attachments.list(page_id=page_id, limit=cap)


@mcp.tool(
    name="attachments_attach",
    annotations={**WRITE, "title": "Attach uploaded files to Wiki page"},
    tags=WRITE_TAGS,
)
def attach(
    page_id: Annotated[int, Field(description="Numeric id of the page to attach to.")],
    session_ids: Annotated[
        list[str],
        Field(description="``session_id`` of each FINISHED upload session to attach."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> AttachedFileList:
    """Attach file(s) from finished upload sessions to a wiki page.

    The final step of the upload pipeline: create the session (``uploadsessions_create``),
    send the bytes (``uploadsessions_upload_part``), close it (``uploadsessions_finish``),
    then attach here. For one small file, ``attachments_upload`` runs the whole pipeline in
    a single call. Returns the newly-attached files.

    Example:
        >>> attach(page_id=12345, session_ids=["1e5c…"])  # doctest: +SKIP
    """
    return client.attachments.attach(page_id, session_ids)


@mcp.tool(
    name="attachments_upload",
    annotations={**WRITE, "title": "Upload file to Wiki page"},
    tags=WRITE_TAGS,
)
def upload(
    page_id: Annotated[int, Field(description="Numeric id of the page to attach the file to.")],
    file_name: Annotated[str, Field(description="Name to give the uploaded file.")],
    data: Annotated[Base64Bytes, Field(description="The file's bytes, base64-encoded.")],
    client: WikiClient = Depends(wiki_client),
) -> AttachedFileList:
    """Upload one small file and attach it to a wiki page in a single call.

    Runs the whole pipeline end to end: opens an upload session sized to ``data``, PUTs the
    bytes as a single part, finishes the session, and attaches it to the page. Small-file
    path — for large files drive ``uploadsessions_create`` / ``uploadsessions_upload_part``
    (chunked) / ``uploadsessions_finish`` + ``attachments_attach`` yourself. Returns the
    newly-attached files.

    Example:
        >>> upload(page_id=12345, file_name="d.txt", data="aGk=")  # doctest: +SKIP
    """
    return client.attachments.upload(client.uploadsessions, page_id, file_name=file_name, data=data)


@mcp.tool(
    name="attachments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Wiki attachment"},
    tags=WRITE_TAGS,
)
def delete(
    page_id: Annotated[int, Field(description="Numeric id of the page the file is attached to.")],
    file_id: Annotated[int, Field(description="Numeric id of the attachment to delete.")],
    client: WikiClient = Depends(wiki_client),
) -> Ack:
    """Delete an attachment from a wiki page — irreversible (no recovery token).

    The API answers ``204 No Content``; a typed acknowledgement is returned instead. Find
    ``file_id`` with ``attachments_list`` and double-check it before calling.

    Example:
        >>> delete(page_id=12345, file_id=678)  # doctest: +SKIP
    """
    client.attachments.delete(page_id=page_id, file_id=file_id)
    return Ack.deleted("attachment", file_id, from_=f"page {page_id}")
