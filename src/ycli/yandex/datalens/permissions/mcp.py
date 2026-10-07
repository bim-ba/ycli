"""DataLens permissions FastMCP tools (read-only) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import RO, datalens_client, new_server
from ycli.yandex.datalens.permissions.models import PermissionsBulk

mcp = new_server("datalens-permissions")


@mcp.tool(
    name="permissions_get_bulk",
    annotations={**RO, "title": "Get DataLens permissions on many objects"},
)
def get_bulk(
    entry_ids: Annotated[list[str] | None, Field(description="Ids of entries.")] = None,
    workbook_ids: Annotated[list[str] | None, Field(description="Ids of workbooks.")] = None,
    collection_ids: Annotated[list[str] | None, Field(description="Ids of collections.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> PermissionsBulk:
    """What the caller may do with many entries, workbooks and collections, in one call.

    Each of the three maps is keyed by id: an object the caller can see gives ``permissions``,
    one that does not exist gives ``error: "NOT_FOUND"``.
    """
    return client.permissions.get_bulk(
        entry_ids=entry_ids, workbook_ids=workbook_ids, collection_ids=collection_ids
    )
