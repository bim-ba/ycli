"""Tracker queue macros FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

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
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)
from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroList, MacroUpdate

mcp = FastMCP("tracker-macros")


@mcp.tool(name="macros_list", annotations={**RO, "title": "List Tracker queue macros"}, tags=TAGS)
def list_(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> MacroList:
    """Every macro configured on a queue — each a canned comment plus field updates.

    Each item's ``id`` is what you pass to ``macros_get`` for the full body and issueUpdate
    rows.

    Example:
        >>> macros_list("TEST")  # doctest: +SKIP
    """
    return client.macros.list(queue_id)


@mcp.tool(name="macros_get", annotations={**RO, "title": "Get Tracker queue macro"}, tags=TAGS)
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

    Example:
        >>> macros_get("TEST", 3)  # doctest: +SKIP
    """
    return client.macros.get(queue_id, macro_id)


@mcp.tool(
    name="macros_create",
    annotations={**WRITE, "title": "Create Tracker queue macro"},
    tags=WRITE_TAGS,
)
def create(
    queue_id: str, body: MacroCreate, client: TrackerClient = Depends(tracker_client)
) -> Macro:
    """Create a macro on a queue (a canned comment plus field updates applied on demand).

    ``name`` is required; optional fields are ``body`` (the comment template) and
    ``fieldChanges`` rows. Returns the new macro.
    """
    return client.macros.create(queue_id, body)


@mcp.tool(
    name="macros_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker queue macro"},
    tags=WRITE_TAGS,
)
def edit(
    queue_id: str,
    macro_id: int,
    body: MacroUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Macro:
    """Edit a queue macro; only the fields set in ``body`` are changed.

    Get ``macro_id`` from ``macros_list``. Returns the updated macro.
    """
    return client.macros.edit(queue_id, macro_id, body)


@mcp.tool(
    name="macros_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker queue macro"},
    tags=WRITE_TAGS,
)
def delete(queue_id: str, macro_id: int, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete a macro from a queue (irreversible).

    Returns an acknowledgement on success.
    """
    client.macros.delete(queue_id, macro_id)
    return Ack(detail=f"deleted macro {macro_id} in queue {queue_id}")
