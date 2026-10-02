"""Tracker issue-attachments FastMCP tools: list, get, delete and base64 uploads.

Downloading an attachment's or thumbnail's raw bytes is CLI/SDK-only (a base64 blob is not a
useful MCP payload). The upload direction is exposed: an agent supplies a small file as base64.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Base64Bytes, Field

from ycli.yandex.models import Ack
from ycli.yandex.tracker.attachments.models import Attachment, AttachmentList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    tracker_client,
)

mcp = FastMCP("tracker-attachments")


@mcp.tool(
    name="attachments_list",
    annotations={**RO, "title": "List Tracker issue attachments"},
    tags=TAGS,
)
def list_(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    client: TrackerClient = Depends(tracker_client),
) -> AttachmentList:
    """Files attached to a Tracker issue — name, size, MIME type, uploader, download URLs.

    Returns metadata only (an ``AttachmentList``); use it to discover a file's id and name.
    Downloading the file's or thumbnail's raw bytes is CLI/SDK-only — run
    ``ycli tracker attachments download <ISSUE> <FILE_ID> <FILENAME>`` — because binary blobs
    are not an MCP payload.

    Example:
        >>> attachments_list("JUNE-2")  # doctest: +SKIP
    """
    return client.attachments.list(issue_key)


@mcp.tool(
    name="attachments_get",
    annotations={**RO, "title": "Get Tracker attachment metadata"},
    tags=TAGS,
)
def get(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    file_id: Annotated[str, Field(description="Attachment file id, from ``attachments_list``.")],
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """One attachment's metadata (name, size, MIME type, uploader, download URL).

    Downloading the bytes is CLI/SDK-only: ``ycli tracker attachments download``.

    Example:
        >>> attachments_get("JUNE-2", "4159")  # doctest: +SKIP
    """
    return client.attachments.get(issue_key, file_id)


@mcp.tool(
    name="attachments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue attachment"},
    tags=WRITE_TAGS,
)
def delete(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    file_id: Annotated[str, Field(description="Attachment file id, from ``attachments_list``.")],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete one attachment from a Tracker issue (irreversible).

    Get ``file_id`` from ``attachments_list``. Returns an acknowledgement on success.
    """
    client.attachments.delete(issue_key, file_id)
    return Ack.deleted("attachment", file_id, on=issue_key)


@mcp.tool(
    name="attachments_upload",
    annotations={**WRITE, "title": "Attach file to Tracker issue"},
    tags=WRITE_TAGS,
)
def upload(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    file_name: Annotated[str, Field(description="Name of the file being uploaded.")],
    data: Annotated[Base64Bytes, Field(description="The file's bytes, base64-encoded.")],
    rename_to: Annotated[
        str | None, Field(description="Store the file under this name instead of ``file_name``.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """Attach a small file to a Tracker issue; returns the created attachment.

    The file travels as base64 in the request, so keep it small; for a large file run
    ``ycli tracker attachments upload`` instead.

    Example:
        >>> attachments_upload("JUNE-2", "a.txt", "aGk=")  # doctest: +SKIP
    """
    return client.attachments.upload(issue_key, filename=file_name, data=data, rename_to=rename_to)


@mcp.tool(
    name="attachments_upload_temp",
    annotations={**WRITE, "title": "Upload temporary Tracker file"},
    tags=WRITE_TAGS,
)
def upload_temp(
    file_name: Annotated[str, Field(description="Name of the file being uploaded.")],
    data: Annotated[Base64Bytes, Field(description="The file's bytes, base64-encoded.")],
    rename_to: Annotated[
        str | None, Field(description="Store the file under this name instead of ``file_name``.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """Upload a small temporary file to attach when creating an issue or a comment.

    The returned ``id`` goes into ``attachmentIds`` of the issue or comment body, and works
    once. The file travels as base64 in the request, so keep it small.

    Example:
        >>> attachments_upload_temp("a.txt", "aGk=")  # doctest: +SKIP
    """
    return client.attachments.upload_temp(filename=file_name, data=data, rename_to=rename_to)
