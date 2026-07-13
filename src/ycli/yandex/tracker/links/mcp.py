"""Tracker issue-links FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    tracker_client,
)
from ycli.yandex.tracker.links.models import Link, LinkCreate, LinkList

mcp = FastMCP("tracker-links")


@mcp.tool(name="links_list", annotations={**RO, "title": "List Tracker issue links"}, tags=TAGS)
def list_(key: str, client: TrackerClient = Depends(tracker_client)) -> LinkList:
    """All links on a Tracker issue (linked issues, type, direction)."""
    return client.links.list(key)


@mcp.tool(name="links_add", annotations={**WRITE, "title": "Link Tracker issues"}, tags=WRITE_TAGS)
def add(key: str, body: LinkCreate, client: TrackerClient = Depends(tracker_client)) -> Link:
    """Link a Tracker issue to another issue; returns the created link."""
    return client.links.add(key, body.model_dump(exclude_none=True))


@mcp.tool(
    name="links_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue link"},
    tags=WRITE_TAGS,
)
def delete(key: str, link_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Remove a link between two Tracker issues (irreversible).

    Get ``link_id`` from ``links_list``. Returns an acknowledgement on success.
    """
    client.links.delete(key, link_id)
    return Ack(detail=f"deleted link {link_id} on {key}")
