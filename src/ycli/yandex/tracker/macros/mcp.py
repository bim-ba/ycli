"""Tracker queue macros FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.macros.models import Macro, MacroList

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
    rows. Creating/editing macros is a write, so it lives on the CLI/SDK only.

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
