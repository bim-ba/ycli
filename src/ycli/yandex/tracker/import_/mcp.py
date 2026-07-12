"""Tracker data-import FastMCP tools (writes, ARCH-3 honest annotations).

Every import endpoint is an admin-only WRITE that back-fills historical data (original
``createdAt`` / ``createdBy`` are preserved). Tool names carry the ``import_<what>`` verb so
the fail-closed ARCH-3 verb map classifies them as writes.
"""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment
from ycli.yandex.tracker.dependencies import WRITE, WRITE_TAGS, tracker_client
from ycli.yandex.tracker.issues.models import Issue
from ycli.yandex.tracker.links.models import Link
from ycli.yandex.tracker.worklog.models import WorklogList

mcp = FastMCP("tracker-import")


@mcp.tool(
    name="import_task", annotations={**WRITE, "title": "Import Tracker issue"}, tags=WRITE_TAGS
)
def task(body: dict, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """Import an issue preserving its original history (admin-only back-fill).

    ``body`` is the raw API payload — required ``queue``, ``summary``, ``createdAt``
    (``YYYY-MM-DDThh:mm:ss.sss±hhmm``) and ``createdBy``; optional ``key``, ``description``,
    ``assignee`` etc. Returns the imported issue.
    """
    return client.import_.task(body=body)


@mcp.tool(
    name="import_comment",
    annotations={**WRITE, "title": "Import Tracker issue comment"},
    tags=WRITE_TAGS,
)
def comment(issue_key: str, body: dict, client: TrackerClient = Depends(tracker_client)) -> Comment:
    """Import a comment onto an issue preserving its original author and timestamp (admin-only).

    ``body`` is the raw API payload — required ``text``, ``createdAt`` and ``createdBy``.
    Returns the imported comment.
    """
    return client.import_.comment(issue_key, body=body)


@mcp.tool(
    name="import_link", annotations={**WRITE, "title": "Import Tracker issue link"}, tags=WRITE_TAGS
)
def link(issue_key: str, body: dict, client: TrackerClient = Depends(tracker_client)) -> Link:
    """Import an issue link preserving its original creation metadata (admin-only).

    ``body`` is the raw API payload — required ``relationship`` (link type), ``issue`` (the key
    to link to), ``createdAt`` and ``createdBy``. Returns the imported link.
    """
    return client.import_.link(issue_key, body=body)


@mcp.tool(
    name="import_worklog",
    annotations={**WRITE, "title": "Import Tracker worklog record"},
    tags=WRITE_TAGS,
)
def worklog(
    issue_key: str, body: dict, client: TrackerClient = Depends(tracker_client)
) -> WorklogList:
    """Import a worklog record preserving its original author and timestamps (admin-only).

    ``body`` is the raw API payload — required ``start``, ``duration`` (ISO-8601, e.g. ``PT1H``),
    ``createdAt`` and ``createdBy``; optional ``comment``. Returns the imported record(s) — the
    endpoint answers with a JSON array.
    """
    return client.import_.worklog(issue_key, body=body)


@mcp.tool(
    name="import_file",
    annotations={**WRITE, "title": "Import Tracker issue attachment"},
    tags=WRITE_TAGS,
)
def file(
    issue_key: str,
    filename: str,
    created_at: str,
    created_by: str,
    data: str,
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
