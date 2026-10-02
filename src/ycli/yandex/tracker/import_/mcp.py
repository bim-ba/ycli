"""Tracker data-import FastMCP tools (writes, ARCH-3 honest annotations).

Every import endpoint is an admin-only WRITE that back-fills historical data (original
``createdAt`` / ``createdBy`` are preserved). Tool names carry the ``import_<what>`` verb so
the fail-closed ARCH-3 verb map classifies them as writes.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment
from ycli.yandex.tracker.dependencies import (
    WRITE,
    WRITE_TAGS,
    IssueKey,
    tracker_client,
)
from ycli.yandex.tracker.import_.models import ImportComment, ImportLink, ImportTask, ImportWorklog
from ycli.yandex.tracker.issues.models import Issue
from ycli.yandex.tracker.links.models import Link
from ycli.yandex.tracker.worklog.models import WorklogList

mcp = FastMCP("tracker-import")


@mcp.tool(
    name="import_task", annotations={**WRITE, "title": "Import Tracker issue"}, tags=WRITE_TAGS
)
def task(body: ImportTask, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """Import an issue preserving its original history (admin-only back-fill).

    Returns the imported issue.
    """
    return client.import_.task(body=body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="import_comment",
    annotations={**WRITE, "title": "Import Tracker issue comment"},
    tags=WRITE_TAGS,
)
def comment(
    issue_key: IssueKey, body: ImportComment, client: TrackerClient = Depends(tracker_client)
) -> Comment:
    """Import a comment onto an issue preserving its original author and timestamp (admin-only).

    Returns the imported comment.
    """
    return client.import_.comment(issue_key, body=body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="import_link", annotations={**WRITE, "title": "Import Tracker issue link"}, tags=WRITE_TAGS
)
def link(
    issue_key: IssueKey, body: ImportLink, client: TrackerClient = Depends(tracker_client)
) -> Link:
    """Import an issue link preserving its original creation metadata (admin-only).

    Returns the imported link.
    """
    return client.import_.link(issue_key, body=body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="import_worklog",
    annotations={**WRITE, "title": "Import Tracker worklog record"},
    tags=WRITE_TAGS,
)
def worklog(
    issue_key: IssueKey, body: ImportWorklog, client: TrackerClient = Depends(tracker_client)
) -> WorklogList:
    """Import a worklog record preserving its original author and timestamps (admin-only).

    Returns the imported record(s) — the endpoint answers with a JSON array.
    """
    return client.import_.worklog(issue_key, body=body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="import_file",
    annotations={**WRITE, "title": "Import Tracker issue attachment"},
    tags=WRITE_TAGS,
)
def file(
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
    CLI (``ycli tracker import file``), which reads raw bytes from disk. ``created_at`` uses
    ``YYYY-MM-DDThh:mm:ss.sss±hhmm``. Returns the imported attachment.
    """
    return client.import_.file(
        issue_key,
        filename=filename,
        created_at=created_at,
        created_by=created_by,
        data=data.encode("utf-8"),
    )
