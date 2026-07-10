"""Tracker issue remote-links FastMCP tool — read-only, LIST ONLY.

Creating and deleting external links are writes and ship on the CLI/SDK only (ARCH-3); only
the list of an issue's remote links is exposed here.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.remotelinks.models import RemoteLinkList

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
    ``links_list``. Creating/deleting remote links is CLI/SDK only (writes, ARCH-3).

    Example:
        >>> remotelinks_list("JUNE-2")  # doctest: +SKIP
    """
    return client.remotelinks.list(issue_key)
