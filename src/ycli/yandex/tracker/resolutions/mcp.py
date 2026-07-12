"""Tracker resolutions FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)
from ycli.yandex.tracker.resolutions.models import (
    Resolution,
    ResolutionCreate,
    ResolutionList,
    ResolutionUpdate,
)

mcp = FastMCP("tracker-resolutions")


@mcp.tool(
    name="resolutions_list", annotations={**RO, "title": "List Tracker resolutions"}, tags=TAGS
)
def list_(client: TrackerClient = Depends(tracker_client)) -> ResolutionList:
    """Every issue resolution configured in the organisation (the close-out result such as
    fixed/duplicate/won't-fix). Use this to resolve or validate a resolution key when reading a
    closed issue or filtering; see ``statuses_list`` for workflow stages, not close-out reasons.

    >>> resolutions_list()  # doctest: +SKIP
    """
    return client.resolutions.list()


@mcp.tool(
    name="resolutions_create",
    annotations={**WRITE, "title": "Create Tracker resolution"},
    tags=WRITE_TAGS,
)
def create(body: ResolutionCreate, client: TrackerClient = Depends(tracker_client)) -> Resolution:
    """Create an org-global issue resolution (a close-out reason such as fixed/duplicate).

    CAUTION: resolutions are organisation-wide and have no delete endpoint — creation leaves
    permanent residue. ``key`` is the latin identifier; ``name`` holds the ru/en display names.
    """
    return client.resolutions.create(body)


@mcp.tool(
    name="resolutions_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker resolution"},
    tags=WRITE_TAGS,
)
def edit(
    resolution_id: str,
    body: ResolutionUpdate,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> Resolution:
    """Edit an issue resolution; only the fields set in ``body`` are changed.

    ``resolution_id`` is the numeric id (not the key). Pass ``version`` to guard against
    concurrent edits (optimistic locking).
    """
    return client.resolutions.edit(resolution_id, body, version=version)
