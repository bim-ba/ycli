"""Tracker issue remote-links FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

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
from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkCreate, RemoteLinkList

mcp = FastMCP("tracker-remotelinks")


@mcp.tool(
    name="remotelinks_list",
    annotations={**RO, "title": "List Tracker issue remote links"},
    tags=TAGS,
)
def list_(
    issue_key: Annotated[str, Field(description="Issue key or id, e.g. ``JUNE-2``.")],
    client: TrackerClient = Depends(tracker_client),
) -> RemoteLinkList:
    """Links from a Tracker issue to objects in external applications (Bitbucket, etc.).

    Each entry carries the link type, direction, and the external object's key plus its owning
    application. This is the *external* link list — for issue-to-issue links use
    ``links_list``.

    Example:
        >>> remotelinks_list("JUNE-2")  # doctest: +SKIP
    """
    return client.remotelinks.list(issue_key)


@mcp.tool(
    name="remotelinks_create",
    annotations={**WRITE, "title": "Create Tracker issue remote link"},
    tags=WRITE_TAGS,
)
def create(
    issue_key: str,
    body: RemoteLinkCreate,
    backlink: str | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> RemoteLink:
    """Link a Tracker issue to an object in an external application; returns the created link.

    Get the application id (``origin``) from ``applications_list``. Pass ``backlink="true"``
    to also create the mirror link in the external app.
    """
    return client.remotelinks.create(
        issue_key, body.model_dump(exclude_none=True), backlink=backlink
    )


@mcp.tool(
    name="remotelinks_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue remote link"},
    tags=WRITE_TAGS,
)
def delete(issue_key: str, link_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Remove a remote (external-application) link from a Tracker issue (irreversible).

    Get ``link_id`` from ``remotelinks_list``. Returns an acknowledgement on success.
    """
    client.remotelinks.delete(issue_key, link_id)
    return Ack(detail=f"deleted remote link {link_id} on {issue_key}")
