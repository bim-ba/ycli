"""Tracker resolutions FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    Version,
    tracker_client,
)
from ycli.yandex.tracker.resolutions.models import Resolution, ResolutionCreate, ResolutionUpdate

mcp = FastMCP("tracker-resolutions")


@mcp.tool(name="resolutions_list", annotations={**RO, "title": "List Tracker resolutions"})
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[Resolution]:
    """Every issue resolution configured in the organisation.

    A resolution is the close-out result such as fixed/duplicate/won't-fix. Use this to resolve
    or validate a resolution key when reading a closed issue or filtering; see ``statuses_list``
    for workflow stages, not close-out reasons.
    """
    return client.resolutions.list()


@mcp.tool(
    name="resolutions_create",
    annotations={**WRITE, "title": "Create Tracker resolution"},
)
def create(body: ResolutionCreate, client: TrackerClient = Depends(tracker_client)) -> Resolution:
    """Create an org-global issue resolution (a close-out reason such as fixed/duplicate).

    CAUTION: resolutions are organisation-wide and have no delete endpoint — creation leaves
    permanent residue. ``key`` is the latin identifier; ``name`` holds the ru/en display names.
    """
    return client.resolutions.create(body)


@mcp.tool(
    name="resolutions_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker resolution"},
)
def update(
    resolution_id: Annotated[
        str, Field(description="Resolution id or key, from ``resolutions_list``.")
    ],
    body: ResolutionUpdate,
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> Resolution:
    """Edit an issue resolution; only the fields set in ``body`` are changed.

    ``resolution_id`` is the numeric id (not the key). Pass ``version`` to guard against
    concurrent edits (optimistic locking).
    """
    return client.resolutions.update(resolution_id, body, version=version)
