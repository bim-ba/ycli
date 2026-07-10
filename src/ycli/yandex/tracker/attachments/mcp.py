"""Tracker issue-attachments FastMCP tool — read-only, LIST ONLY.

Only the attachment *list* is exposed here. Downloading an attachment's or thumbnail's raw
bytes is CLI/SDK-only (a base64 blob is not a useful MCP payload), so this module imports and
mounts NO write/binary method — just ``AttachmentsClient.list``.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.attachments.models import AttachmentList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client

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
