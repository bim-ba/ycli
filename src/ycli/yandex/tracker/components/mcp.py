"""Tracker components FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.components.models import (
    Component,
    ComponentCreate,
    ComponentGroupAccess,
    ComponentUpdate,
    ComponentUserAccess,
)
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    Version,
    tracker_client,
)

mcp = FastMCP("tracker-components")


@mcp.tool(name="components_list", annotations={**RO, "title": "List Tracker components"})
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[Component]:
    """All components created by the organisation's users.

    Each component carries its queue, owner and description. Components are sub-areas used to
    classify issues within a queue; use this to discover valid component names/ids before
    filtering or creating issues.
    """
    return client.components.list()


@mcp.tool(
    name="components_create",
    annotations={**WRITE, "title": "Create Tracker component"},
)
def create(body: ComponentCreate, client: TrackerClient = Depends(tracker_client)) -> Component:
    """Create a component in a queue (a sub-area for classifying its issues).

    ``name`` and ``queue`` (the queue key) are required; optional fields include
    ``description``, ``lead`` and ``assignAuto``.
    """
    return client.components.create(body)


@mcp.tool(
    name="components_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker component"},
)
def update(
    component_id: Annotated[
        int, Field(description="Numeric id of the component, from ``components_list``.")
    ],
    body: ComponentUpdate,
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> Component:
    """Edit a component; only the fields set in ``body`` are changed.

    Get ``component_id`` from ``components_list``. Pass ``version`` to guard against concurrent
    edits (optimistic locking).
    """
    return client.components.update(component_id, body, version=version)


@mcp.tool(
    name="components_list_for_queue",
    annotations={**RO, "title": "List components of a Tracker queue"},
)
def list_for_queue(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    fields: Annotated[
        str | None,
        Field(description="Comma-separated extra fields: ``version,description,lead,assignAuto``."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Component]:
    """The components of one queue, so you need not filter ``components_list`` by queue."""
    return client.components.list_for_queue(queue_id, fields=fields)


@mcp.tool(name="components_get", annotations={**RO, "title": "Get Tracker component"})
def get(
    component_id: Annotated[
        int, Field(description="Numeric id of the component, from ``components_list``.")
    ],
    fields: Annotated[
        str | None,
        Field(description="Comma-separated fields to return, e.g. ``name,description,lead``."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Component:
    """One component with its queue, owner, description and auto-assign flag."""
    return client.components.get(component_id, fields=fields)


@mcp.tool(
    name="components_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker component"},
)
def delete(
    component_id: Annotated[
        int, Field(description="Numeric id of the component, from ``components_list``.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete a component (irreversible). Returns an acknowledgement."""
    client.components.delete(component_id)
    return Ack.deleted("component", component_id)


@mcp.tool(
    name="components_user_permissions_get",
    annotations={**RO, "title": "Get a user's rights on a Tracker component"},
)
def user_permissions_get(
    component_id: Annotated[int, Field(description="Numeric id of the component.")],
    user_id: Annotated[str, Field(description="Login or numeric uid of the user.")],
    client: TrackerClient = Depends(tracker_client),
) -> ComponentUserAccess:
    """What one user may do on a component (create, read, write, deny) and who grants it."""
    return client.components.user_permissions_get(component_id, user_id)


@mcp.tool(
    name="components_group_permissions_get",
    annotations={**RO, "title": "Get a group's rights on a Tracker component"},
)
def group_permissions_get(
    component_id: Annotated[int, Field(description="Numeric id of the component.")],
    group_id: Annotated[int, Field(description="Numeric id of the group.")],
    client: TrackerClient = Depends(tracker_client),
) -> ComponentGroupAccess:
    """What one group may do on a component (create, read, write, deny)."""
    return client.components.group_permissions_get(component_id, group_id)
