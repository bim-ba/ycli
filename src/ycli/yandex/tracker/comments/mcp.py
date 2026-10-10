"""Tracker issue-comments FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, Listed
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment, CommentUpdate, ImportComment
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    All,
    CommentID,
    Expand,
    IssueKey,
    Next,
    app_config,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.models import CommentCreate

mcp = new_server("tracker-comments")


@mcp.tool(name="comments_list", annotations={**RO, "title": "List Tracker issue comments"})
def list_(
    issue_key: IssueKey,
    limit: Annotated[
        int | None,
        Field(ge=1, description=f"Max comments to return; {LIMIT_CAP}"),
    ] = None,
    all: All = False,
    next: Next = None,
    expand: Expand = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Comment]:
    """All comments on a Tracker issue, auto-paginated via the relative id-cursor.

    Capped at the configured item cap unless ``limit`` is given, so very long threads
    are truncated at the cap rather than fetched forever.
    """
    cap = config.http.tool_cap(limit, all_=all)
    return client.comments.list(issue_key, limit=cap, next=next, expand=expand).collect()


@mcp.tool(name="comments_get", annotations={**RO, "title": "Get Tracker issue comment"})
def get(
    issue_key: IssueKey,
    comment_id: CommentID,
    expand: Annotated[
        str | None,
        Field(description="Extra fields: ``attachments``, ``html`` or ``all`` (comma-separated)."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """One comment of a Tracker issue: text, author, edit history and, on request, attachments."""
    return client.comments.get(issue_key, comment_id, expand=expand)


@mcp.tool(
    name="comments_create",
    annotations={**WRITE, "title": "Add Tracker issue comment"},
)
def create(
    issue_key: IssueKey, body: CommentCreate, client: TrackerClient = Depends(tracker_client)
) -> Comment:
    """Add a comment to a Tracker issue; returns the created comment."""
    return client.comments.create(issue_key, body)


@mcp.tool(
    name="comments_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker issue comment"},
)
def update(
    issue_key: IssueKey,
    comment_id: CommentID,
    body: CommentUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Replace the text of an existing comment on a Tracker issue.

    Get ``comment_id`` from ``comments_list``. Returns the updated comment.
    """
    return client.comments.update(issue_key, comment_id, body)


@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue comment"},
)
def delete(
    issue_key: IssueKey, comment_id: CommentID, client: TrackerClient = Depends(tracker_client)
) -> Ack:
    """Permanently delete one comment from a Tracker issue (irreversible).

    Get ``comment_id`` from ``comments_list``. Returns an acknowledgement on success.
    """
    client.comments.delete(issue_key, comment_id)
    return Ack.deleted("comment", comment_id, on=issue_key)


@mcp.tool(
    name="comments_reactions_create",
    annotations={**WRITE, "title": "React to Tracker issue comment"},
)
def reactions_create(
    issue_key: IssueKey,
    comment_id: CommentID,
    name: Annotated[
        str, Field(description="Reaction name, e.g. ``like``, ``dislike`` or ``fire``.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Add an emoji reaction to a comment on a Tracker issue.

    ``name`` is the reaction name (e.g. ``like``, ``dislike``, ``fire``). Returns the comment
    with its updated reactions.
    """
    return client.comments.reactions_create(issue_key, comment_id, name)


@mcp.tool(
    name="comments_import",
    annotations={**WRITE, "title": "Import Tracker issue comment"},
)
def import_(
    issue_key: IssueKey, body: ImportComment, client: TrackerClient = Depends(tracker_client)
) -> Comment:
    """Import a comment onto an issue preserving its original author and timestamp (admin-only).

    Returns the imported comment.
    """
    return client.comments.import_(issue_key, body=body)
