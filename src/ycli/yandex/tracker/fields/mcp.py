"""Tracker global-fields FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    Version,
    tracker_client,
)
from ycli.yandex.tracker.fields.models import (
    CustomField,
    FieldCategoryCreate,
    FieldCategoryRecord,
    FieldCategoryUpdate,
    FieldUpdate,
)
from ycli.yandex.tracker.models import FieldCreate

mcp = FastMCP("tracker-fields")


@mcp.tool(name="fields_list", annotations={**RO, "title": "List Tracker global fields"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> ItemList[CustomField]:
    """All global (organisation-wide) issue fields, both standard and custom.

    Each field carries its value schema, category and provider metadata. Use this to discover
    which field keys exist before filtering or reading issues; use ``fields_get`` when you
    already know one field id.
    """
    return client.fields.list()


@mcp.tool(name="fields_get", annotations={**RO, "title": "Get Tracker field"}, tags=TAGS)
def get(
    field_id: Annotated[
        str, Field(description="Identifier of the issue field, e.g. summary or a custom-field key.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> CustomField:
    """Parameters of a single issue field.

    They include its value schema, read-only flag, allowed options and category. Use this when you
    already know the field id; use ``fields_list`` to enumerate every field in the organisation.
    """
    return client.fields.get(field_id=field_id)


@mcp.tool(
    name="fields_create", annotations={**WRITE, "title": "Create Tracker field"}, tags=WRITE_TAGS
)
def create(body: FieldCreate, client: TrackerClient = Depends(tracker_client)) -> CustomField:
    """Create an org-global custom issue field.

    CAUTION: global fields are organisation-wide and NOT deletable — creation leaves permanent
    residue; prefer ``localfields_create`` for a single queue. Required: ``id`` (latin key),
    ``name`` (ru/en display names), ``category`` (a category id) and ``type`` (value type).
    """
    return client.fields.create(body)


@mcp.tool(
    name="fields_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker field"},
    tags=WRITE_TAGS,
)
def update(
    field_id: Annotated[
        str, Field(description="Identifier of the issue field, from ``fields_list``.")
    ],
    body: FieldUpdate,
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> CustomField:
    """Edit an org-global issue field; only the fields set in ``body`` are changed.

    Pass ``version`` to guard against concurrent edits (optimistic locking). Returns the
    updated field definition.
    """
    return client.fields.update(field_id, body, version=version)


@mcp.tool(
    name="fields_category_create",
    annotations={**WRITE, "title": "Create Tracker field category"},
    tags=WRITE_TAGS,
)
def category_create(
    body: FieldCategoryCreate, client: TrackerClient = Depends(tracker_client)
) -> FieldCategoryRecord:
    """Create a field category (a grouping bucket for issue fields in the UI).

    Required: ``name`` (ru/en display names) and ``order`` (display weight). CAUTION:
    org-global and not deletable via the API.
    """
    return client.fields.category_create(body)


@mcp.tool(
    name="fields_category_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker field category"},
    tags=WRITE_TAGS,
)
def category_update(
    category_id: Annotated[str, Field(description="Identifier of the field category.")],
    body: FieldCategoryUpdate,
    version: Version = None,
    client: TrackerClient = Depends(tracker_client),
) -> FieldCategoryRecord:
    """Edit a field category; only the fields set in ``body`` are changed.

    Pass ``version`` to guard against concurrent edits (optimistic locking).
    """
    return client.fields.category_update(category_id, body, version=version)
