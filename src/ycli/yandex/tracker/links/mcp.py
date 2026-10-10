"""Tracker issue-links FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList, Listed
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    All,
    IssueKey,
    Next,
    app_config,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.links.models import ImportLink, Link, LinkCreate

mcp = new_server("tracker-links")


@mcp.tool(name="links_list", annotations={**RO, "title": "List Tracker issue links"})
def list_(issue_key: IssueKey, client: TrackerClient = Depends(tracker_client)) -> ItemList[Link]:
    """All links on a Tracker issue (linked issues, type, direction)."""
    return client.links.list(issue_key)


@mcp.tool(name="links_list_filtered", annotations={**RO, "title": "Search Tracker issue links"})
def list_filtered(
    issue_key: IssueKey,
    link_types: Annotated[
        list[str] | None,
        Field(
            description=(
                "Keep only links with these relationships, e.g. ``relates`` or "
                "``is subtask for`` (the phrases of ``links_create``, not linktypes ids)."
            )
        ),
    ] = None,
    fields: Annotated[
        list[str] | None, Field(description="Fields to include in each link; all when omitted.")
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max links to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Link]:
    """Links of a Tracker issue filtered by type, paged and capped (a read done via POST).

    Prefer this over ``links_list`` for issues with many links or when only some link types
    or fields matter; it carries each link's author, dates, assignee and status.
    """
    cap = config.http.cap(limit, all_=all)
    return client.links.list_filtered(
        issue_key, link_types=link_types, fields=fields, limit=cap, next=next
    ).collect()


@mcp.tool(name="links_create", annotations={**WRITE, "title": "Link Tracker issues"})
def create(
    issue_key: IssueKey, body: LinkCreate, client: TrackerClient = Depends(tracker_client)
) -> Link:
    """Link a Tracker issue to another issue; returns the created link."""
    return client.links.create(issue_key, body)


@mcp.tool(
    name="links_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue link"},
)
def delete(
    issue_key: IssueKey,
    link_id: Annotated[str, Field(description="Link id, from ``links_list``.")],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Remove a link between two Tracker issues (irreversible).

    Get ``link_id`` from ``links_list``. Returns an acknowledgement on success.
    """
    client.links.delete(issue_key, link_id)
    return Ack.deleted("link", link_id, on=issue_key)


@mcp.tool(name="links_import", annotations={**WRITE, "title": "Import Tracker issue link"})
def import_(
    issue_key: IssueKey, body: ImportLink, client: TrackerClient = Depends(tracker_client)
) -> Link:
    """Import an issue link preserving its original creation metadata (admin-only).

    Returns the imported link.
    """
    return client.links.import_(issue_key, body=body)
