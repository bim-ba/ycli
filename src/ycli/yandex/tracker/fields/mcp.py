"""Tracker global-fields FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, tracker_client
from ycli.yandex.tracker.fields.models import CustomField, FieldList

mcp = FastMCP("tracker-fields")


@mcp.tool(name="fields_list", annotations={**RO, "title": "List Tracker global fields"}, tags=TAGS)
def list_(client: TrackerClient = Depends(tracker_client)) -> FieldList:
    """All global (organisation-wide) issue fields, both standard and custom, each with its
    value schema, category and provider metadata. Use this to discover which field keys exist
    before filtering or reading issues; use ``fields_get`` when you already know one field id.

    >>> fields_list()  # doctest: +SKIP
    """
    return client.fields.list()


@mcp.tool(name="fields_get", annotations={**RO, "title": "Get Tracker field"}, tags=TAGS)
def get(
    field_id: Annotated[
        str, Field(description="Identifier of the issue field, e.g. summary or a custom-field key.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> CustomField:
    """Parameters of a single issue field: its value schema, read-only flag, allowed options and
    category. Use this when you already know the field id; use ``fields_list`` to enumerate every
    field in the organisation.

    >>> fields_get(field_id="ruName")  # doctest: +SKIP
    """
    return client.fields.get(field_id=field_id)
