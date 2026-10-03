"""Tracker issue-links FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    IssueKey,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.links.models import Link, LinkCreate

mcp = FastMCP("tracker-links")


@mcp.tool(name="links_list", annotations={**RO, "title": "List Tracker issue links"}, tags=TAGS)
def list_(key: IssueKey, client: TrackerClient = Depends(tracker_client)) -> ItemList[Link]:
    """All links on a Tracker issue (linked issues, type, direction)."""
    return client.links.list(key)


@mcp.tool(name="links_search", annotations={**RO, "title": "Search Tracker issue links"}, tags=TAGS)
def search(
    key: IssueKey,
    link_types: Annotated[
        list[str] | None,
        Field(
            description=(
                "Keep only links with these relationships, e.g. ``relates`` or "
                "``is subtask for`` (the phrases of ``links_add``, not linktypes ids)."
            )
        ),
    ] = None,
    fields: Annotated[
        list[str] | None, Field(description="Fields to include in each link; all when omitted.")
    ] = None,
    limit: Annotated[int, Field(description=f"Max links to return; {LIMIT_CAP}")] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Link]:
    """Links of a Tracker issue filtered by type, paged and capped (a read done via POST).

    Prefer this over ``links_list`` for issues with many links or when only some link types
    or fields matter; it carries each link's author, dates, assignee and status.
    """
    cap = config.http.cap(limit)
    return client.links.search(key, link_types=link_types, fields=fields, limit=cap)


@mcp.tool(name="links_add", annotations={**WRITE, "title": "Link Tracker issues"}, tags=WRITE_TAGS)
def add(key: IssueKey, body: LinkCreate, client: TrackerClient = Depends(tracker_client)) -> Link:
    """Link a Tracker issue to another issue; returns the created link."""
    return client.links.add(key, body)


@mcp.tool(
    name="links_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue link"},
    tags=WRITE_TAGS,
)
def delete(
    key: IssueKey,
    link_id: Annotated[str, Field(description="Link id, from ``links_list``.")],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Remove a link between two Tracker issues (irreversible).

    Get ``link_id`` from ``links_list``. Returns an acknowledgement on success.
    """
    client.links.delete(key, link_id)
    return Ack.deleted("link", link_id, on=key)
