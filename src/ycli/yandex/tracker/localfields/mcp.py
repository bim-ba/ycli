"""Tracker localFields FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    tracker_client,
)
from ycli.yandex.tracker.localfields.models import (
    LocalField,
    LocalFieldCreate,
    LocalFieldList,
    LocalFieldUpdate,
)

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


@mcp.tool(
    name="localfields_create",
    annotations={**WRITE, "title": "Create Tracker local field"},
    tags=WRITE_TAGS,
)
def create(
    queue_id: str, body: LocalFieldCreate, client: TrackerClient = Depends(tracker_client)
) -> LocalField:
    """Create a custom field scoped to one queue (a local field).

    Required fields: ``id`` (latin key), ``name`` (ru/en display names), ``category`` (a category
    id from ``fields_list``) and ``type`` (value type, e.g. ``ru.yandex.startrek.core.fields.
    StringFieldType``). There is no delete endpoint — the field lives until its queue is deleted.
    """
    return client.localfields.create(queue_id, body)


@mcp.tool(
    name="localfields_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker local field"},
    tags=WRITE_TAGS,
)
def edit(
    queue_id: str,
    field_key: str,
    body: LocalFieldUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> LocalField:
    """Edit a queue-local field; only the fields set in ``body`` are changed.

    Get ``field_key`` from ``localfields_list``. Returns the updated field definition.
    """
    return client.localfields.edit(queue_id, field_key, body)
