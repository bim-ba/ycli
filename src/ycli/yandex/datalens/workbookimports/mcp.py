"""DataLens workbook imports FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import RO, WRITE, datalens_client
from ycli.yandex.datalens.workbookimports.models import (
    WorkbookImportStarted,
    WorkbookImportStatus,
)

mcp = FastMCP("datalens-workbookimports")


@mcp.tool(
    name="workbookimports_start", annotations={**WRITE, "title": "Start DataLens workbook import"}
)
def start(
    data: Annotated[
        dict[str, Any],
        Field(description="The ``data`` of ``workbookexports_result_get``: ``export``, ``hash``."),
    ],
    title: Annotated[str, Field(description="The title of the new workbook.")],
    collection_id: Annotated[
        str | None, Field(description="The collection to make it in; the root when left out.")
    ] = None,
    description: Annotated[
        str | None, Field(description="The description of the new workbook.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> WorkbookImportStarted:
    """Start making a workbook from an export; returns the ids of the import and the workbook.

    The workbook exists at once and is filled as the import runs: ask
    ``workbookimports_status_get`` until ``status`` is ``success``.
    """
    return client.workbookimports.start(
        data, title=title, collection_id=collection_id, description=description
    )


@mcp.tool(
    name="workbookimports_status_get",
    annotations={**RO, "title": "Get DataLens workbook import status"},
)
def status_get(
    import_id: Annotated[str, Field(description="Import id, from ``workbookimports_start``.")],
    client: DataLensClient = Depends(datalens_client),
) -> WorkbookImportStatus:
    """How far an import is: ``pending``, ``success`` or ``error``, and the progress in percent.

    ``notifications`` holds what the import has to say about an entry: id, level, message.
    """
    return client.workbookimports.status_get(import_id)
