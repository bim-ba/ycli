"""Tracker issue-comments FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment, CommentUpdate
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    CommentId,
    Expand,
    IssueKey,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.models import CommentCreate

mcp = FastMCP("tracker-comments")


@mcp.tool(
    name="comments_list", annotations={**RO, "title": "List Tracker issue comments"}, tags=TAGS
)
def list_(
    key: IssueKey,
    limit: Annotated[
        int | None,
        Field(ge=1, description=f"Max comments to return; {LIMIT_CAP}"),
    ] = None,
    expand: Expand = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Comment]:
    """All comments on a Tracker issue, auto-paginated via the relative id-cursor.

    Capped at the configured item cap unless ``limit`` is given, so very long threads
    are truncated at the cap rather than fetched forever.
    """
    cap = config.http.cap(limit)
    return client.comments.list(key, limit=cap, expand=expand)


@mcp.tool(name="comments_get", annotations={**RO, "title": "Get Tracker issue comment"}, tags=TAGS)
def get(
    key: IssueKey,
    comment_id: Annotated[
        str, Field(description="Comment id (numeric ``id`` or ``longId``), from ``comments_list``.")
    ],
    expand: Annotated[
        str | None,
        Field(description="Extra fields: ``attachments``, ``html`` or ``all`` (comma-separated)."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """One comment of a Tracker issue: text, author, edit history and, on request, attachments."""
    return client.comments.get(key, comment_id, expand=expand)


@mcp.tool(
    name="comments_add",
    annotations={**WRITE, "title": "Add Tracker issue comment"},
    tags=WRITE_TAGS,
)
def add(
    key: IssueKey, body: CommentCreate, client: TrackerClient = Depends(tracker_client)
) -> Comment:
    """Add a comment to a Tracker issue; returns the created comment."""
    return client.comments.add(key, body)


@mcp.tool(
    name="comments_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker issue comment"},
    tags=WRITE_TAGS,
)
def update(
    key: IssueKey,
    comment_id: CommentId,
    body: CommentUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Replace the text of an existing comment on a Tracker issue.

    Get ``comment_id`` from ``comments_list``. Returns the updated comment.
    """
    return client.comments.update(key, comment_id, body)


@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue comment"},
    tags=WRITE_TAGS,
)
def delete(
    key: IssueKey, comment_id: CommentId, client: TrackerClient = Depends(tracker_client)
) -> Ack:
    """Permanently delete one comment from a Tracker issue (irreversible).

    Get ``comment_id`` from ``comments_list``. Returns an acknowledgement on success.
    """
    client.comments.delete(key, comment_id)
    return Ack.deleted("comment", comment_id, on=key)


@mcp.tool(
    name="comments_react",
    annotations={**WRITE, "title": "React to Tracker issue comment"},
    tags=WRITE_TAGS,
)
def react(
    key: IssueKey,
    comment_id: CommentId,
    name: Annotated[
        str, Field(description="Reaction name, e.g. ``like``, ``dislike`` or ``fire``.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Add an emoji reaction to a comment on a Tracker issue.

    ``name`` is the reaction name (e.g. ``like``, ``dislike``, ``fire``). Returns the comment
    with its updated reactions.
    """
    return client.comments.react(key, comment_id, name)
