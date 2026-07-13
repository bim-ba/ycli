"""Tracker issue-comments FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment, CommentList
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    app_config,
    tracker_client,
)

mcp = FastMCP("tracker-comments")


@mcp.tool(
    name="comments_list", annotations={**RO, "title": "List Tracker issue comments"}, tags=TAGS
)
def list_(
    key: str,
    limit: Annotated[
        int,
        Field(description="Max comments to return; 0 means the YCLI_MAX_ITEMS cap (default 500)."),
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
    cfg: AppConfig = Depends(app_config),
) -> CommentList:
    """All comments on a Tracker issue, auto-paginated via the relative id-cursor.

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given, so very long threads
    are truncated at the cap rather than fetched forever.
    """
    cap = resolve_cap(limit, cfg.max_items)
    return client.comments.list(key, limit=cap)


@mcp.tool(
    name="comments_add",
    annotations={**WRITE, "title": "Add Tracker issue comment"},
    tags=WRITE_TAGS,
)
def add(key: str, body: dict, client: TrackerClient = Depends(tracker_client)) -> Comment:
    """Add a comment to a Tracker issue; returns the created comment.

    ``body`` is the raw API payload — at minimum ``{"text": "…"}`` (YFM markup allowed);
    optional keys include ``summonees`` (logins to summon) and ``attachmentIds``.
    """
    return client.comments.add(key, body)


@mcp.tool(
    name="comments_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker issue comment"},
    tags=WRITE_TAGS,
)
def edit(
    key: str, comment_id: str, body: dict, client: TrackerClient = Depends(tracker_client)
) -> Comment:
    """Replace the text of an existing comment on a Tracker issue.

    ``body`` is the raw API payload, e.g. ``{"text": "new text"}``. Get ``comment_id`` from
    ``comments_list``. Returns the updated comment.
    """
    return client.comments.edit(key, comment_id, body)


@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue comment"},
    tags=WRITE_TAGS,
)
def delete(key: str, comment_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete one comment from a Tracker issue (irreversible).

    Get ``comment_id`` from ``comments_list``. Returns an acknowledgement on success.
    """
    client.comments.delete(key, comment_id)
    return Ack(detail=f"deleted comment {comment_id} on {key}")


@mcp.tool(
    name="comments_react",
    annotations={**WRITE, "title": "React to Tracker issue comment"},
    tags=WRITE_TAGS,
)
def react(
    key: str, comment_id: str, name: str, client: TrackerClient = Depends(tracker_client)
) -> Comment:
    """Add an emoji reaction to a comment on a Tracker issue.

    ``name`` is the reaction name (e.g. ``like``, ``dislike``, ``fire``). Returns the comment
    with its updated reactions.
    """
    return client.comments.react(key, comment_id, name)
