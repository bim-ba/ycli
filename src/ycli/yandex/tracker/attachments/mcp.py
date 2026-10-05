"""Tracker issue-attachments FastMCP tools: list, get, delete and base64 uploads.

Downloading an attachment's or thumbnail's raw bytes is CLI/SDK-only (a base64 blob is not a
useful MCP payload). The upload direction is exposed: an agent supplies a small file as base64.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Base64Bytes, Field

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    IssueKey,
    tracker_client,
)

mcp = FastMCP("tracker-attachments")


@mcp.tool(
    name="attachments_list",
    annotations={**RO, "title": "List Tracker issue attachments"},
)
def list_(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Attachment]:
    """Files attached to a Tracker issue — name, size, MIME type, uploader, download URLs.

    Returns metadata only (an ``ItemList[Attachment]``); use it to discover a file's id and name.
    Downloading the file's or thumbnail's raw bytes is CLI/SDK-only — run
    ``ycli tracker attachments download <ISSUE> <FILE_ID> <FILENAME>`` — because binary blobs
    are not an MCP payload.
    """
    return client.attachments.list(issue_key)


@mcp.tool(
    name="attachments_get",
    annotations={**RO, "title": "Get Tracker attachment metadata"},
)
def get(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    file_id: Annotated[str, Field(description="Attachment file id, from ``attachments_list``.")],
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """One attachment's metadata (name, size, MIME type, uploader, download URL).

    Downloading the bytes is CLI/SDK-only: ``ycli tracker attachments download``.
    """
    return client.attachments.get(issue_key, file_id)


@mcp.tool(
    name="attachments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue attachment"},
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
)
def upload(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    filename: Annotated[str, Field(description="Name of the file being uploaded.")],
    data: Annotated[Base64Bytes, Field(description="The file's bytes, base64-encoded.")],
    rename_to: Annotated[
        str | None, Field(description="Store the file under this name instead of ``filename``.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """Attach a small file to a Tracker issue; returns the created attachment.

    The file travels as base64 in the request, so keep it small; for a large file run
    ``ycli tracker attachments upload`` instead.
    """
    return client.attachments.upload(issue_key, filename=filename, data=data, rename_to=rename_to)


@mcp.tool(
    name="attachments_upload_temp",
    annotations={**WRITE, "title": "Upload temporary Tracker file"},
)
def upload_temp(
    filename: Annotated[str, Field(description="Name of the file being uploaded.")],
    data: Annotated[Base64Bytes, Field(description="The file's bytes, base64-encoded.")],
    rename_to: Annotated[
        str | None, Field(description="Store the file under this name instead of ``filename``.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """Upload a small temporary file to attach when creating an issue or a comment.

    The returned ``id`` goes into ``attachmentIds`` of the issue or comment body, and works
    once. The file travels as base64 in the request, so keep it small.
    """
    return client.attachments.upload_temp(filename=filename, data=data, rename_to=rename_to)


@mcp.tool(
    name="attachments_import",
    annotations={**WRITE, "title": "Import Tracker issue attachment"},
)
def import_(
    issue_key: IssueKey,
    filename: Annotated[str, Field(description="Name the imported file gets on the issue.")],
    created_at: Annotated[
        str, Field(description="Original creation time, ``YYYY-MM-DDThh:mm:ss.sss±hhmm``.")
    ],
    created_by: Annotated[
        str, Field(description="Login or id of the user to record as the file's author.")
    ],
    data: Annotated[
        str, Field(description="File content as UTF-8 text (binary files: use the CLI).")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """Import a text-file attachment onto an issue preserving its original metadata (admin-only).

    ``data`` is the file content as text (UTF-8-encoded on upload) — for binary files use the
    CLI (``ycli tracker attachments import``), which reads raw bytes from disk. ``created_at`` uses
    ``YYYY-MM-DDThh:mm:ss.sss±hhmm``. Returns the imported attachment.
    """
    return client.attachments.import_(
        issue_key,
        filename=filename,
        created_at=created_at,
        created_by=created_by,
        data=data.encode("utf-8"),
    )
