"""Tracker queue macros FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    MacroID,
    QueueID,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroUpdate

mcp = new_server("tracker-macros")


@mcp.tool(name="macros_list", annotations={**RO, "title": "List Tracker queue macros"})
def list_(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Macro]:
    """Every macro configured on a queue — each a canned comment plus field updates.

    Each item's ``id`` is what you pass to ``macros_get`` for the full body and issueUpdate
    rows.
    """
    return client.macros.list(queue_id)


@mcp.tool(name="macros_get", annotations={**RO, "title": "Get Tracker queue macro"})
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    macro_id: Annotated[int, Field(description="Numeric identifier of the macro.")],
    client: TrackerClient = Depends(tracker_client),
) -> Macro:
    """One queue macro by id — its comment body and the field updates it applies.

    Sibling ``macros_list`` enumerates every macro in the queue; pass one of its ``id`` values
    here.
    """
    return client.macros.get(queue_id, macro_id)


@mcp.tool(
    name="macros_create",
    annotations={**WRITE, "title": "Create Tracker queue macro"},
)
def create(
    queue_id: QueueID, body: MacroCreate, client: TrackerClient = Depends(tracker_client)
) -> Macro:
    """Create a macro on a queue (a canned comment plus field updates applied on demand).

    ``name`` is required; optional fields are ``body`` (the comment template) and
    ``fieldChanges`` rows. Returns the new macro.
    """
    return client.macros.create(queue_id, body)


@mcp.tool(
    name="macros_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker queue macro"},
)
def update(
    queue_id: QueueID,
    macro_id: MacroID,
    body: MacroUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Macro:
    """Edit a queue macro; only the fields set in ``body`` are changed.

    Get ``macro_id`` from ``macros_list``. Returns the updated macro.
    """
    return client.macros.update(queue_id, macro_id, body)


@mcp.tool(
    name="macros_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker queue macro"},
)
def delete(
    queue_id: QueueID, macro_id: MacroID, client: TrackerClient = Depends(tracker_client)
) -> Ack:
    """Permanently delete a macro from a queue (irreversible).

    Returns an acknowledgement on success.
    """
    client.macros.delete(queue_id, macro_id)
    return Ack.deleted("macro", macro_id, from_=f"queue {queue_id}")
