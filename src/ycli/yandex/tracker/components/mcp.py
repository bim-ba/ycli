"""Tracker components FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.components.models import (
    Component,
    ComponentCreate,
    ComponentList,
    ComponentUpdate,
)
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)

mcp = FastMCP("tracker-components")


@mcp.tool(name="components_list", annotations={**RO, "title": "List Tracker components"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> ComponentList:
    """All components created by the organisation's users, each with its queue, owner and
    description. Components are sub-areas used to classify issues within a queue; use this to
    discover valid component names/ids before filtering or creating issues.

    >>> components_list()  # doctest: +SKIP
    """
    return client.components.list()


@mcp.tool(
    name="components_create",
    annotations={**WRITE, "title": "Create Tracker component"},
    tags=WRITE_TAGS,
)
def create(body: ComponentCreate, client: TrackerClient = Depends(tracker_client)) -> Component:
    """Create a component in a queue (a sub-area for classifying its issues).

    ``name`` and ``queue`` (the queue key) are required; optional fields include
    ``description``, ``lead`` and ``assignAuto``. CAUTION: components have no delete endpoint —
    they persist until their queue is deleted.
    """
    return client.components.create(body)


@mcp.tool(
    name="components_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker component"},
    tags=WRITE_TAGS,
)
def edit(
    component_id: int,
    body: ComponentUpdate,
    version: int | None = None,
    client: TrackerClient = Depends(tracker_client),
) -> Component:
    """Edit a component; only the fields set in ``body`` are changed.

    Get ``component_id`` from ``components_list``. Pass ``version`` to guard against concurrent
    edits (optimistic locking).
    """
    return client.components.edit(component_id, body, version=version)
