"""Tracker localFields FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.localfields.models import LocalField, LocalFieldList

mcp = FastMCP("tracker-localfields")


@mcp.tool(
    name="localfields_list", annotations={**RO, "title": "List Tracker local fields"}, tags=TAGS
)
def list_(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. ORG) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> LocalFieldList:
    """Custom fields scoped to one queue (its local fields), as a flat list.

    Each item's ``key`` is the field key you pass to ``localfields_get``; ``field_schema``
    describes the value type. Local fields differ from global fields (``fields_list``) in that
    they exist only inside the given queue. Pass a ``key`` from ``queues_list`` as ``queue_id``.

    Example:
        >>> localfields_list("ORG")  # doctest: +SKIP
    """
    return client.localfields.list(queue_id)


@mcp.tool(name="localfields_get", annotations={**RO, "title": "Get Tracker local field"}, tags=TAGS)
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. ORG) or numeric queue id.")
    ],
    field_key: Annotated[
        str, Field(description="Local field key, as returned by localfields_list.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> LocalField:
    """One local field's full definition (type, options, category) by queue and field key.

    Raises if the field is not found. Returns the value schema, allowed-values provider and
    category of the field. Use ``localfields_list`` first to discover the ``field_key`` values
    available in a queue.

    Example:
        >>> localfields_get("ORG", "loc_field_key")  # doctest: +SKIP
    """
    result = client.localfields.get(queue_id, field_key)
    if result.key is None and result.id is None:
        raise ValueError(
            f"local field {field_key!r} not found in queue {queue_id!r} "
            "(got empty response — check keys or permissions)"
        )
    return result
