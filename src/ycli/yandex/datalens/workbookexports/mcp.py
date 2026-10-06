"""DataLens workbook exports FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import RO, WRITE, WRITE_IDEMPOTENT, datalens_client
from ycli.yandex.datalens.workbookexports.models import (
    WorkbookExport,
    WorkbookExportCancelled,
    WorkbookExportStarted,
    WorkbookExportStatus,
)

mcp = FastMCP("datalens-workbookexports")

ExportID = Annotated[str, Field(description="Export id, from ``workbookexports_start``.")]


@mcp.tool(
    name="workbookexports_start", annotations={**WRITE, "title": "Start DataLens workbook export"}
)
def start(
    workbook_id: Annotated[str, Field(description="Workbook id.")],
    client: DataLensClient = Depends(datalens_client),
) -> WorkbookExportStarted:
    """Start exporting a workbook and return the id of the export.

    The export runs on its own: ask ``workbookexports_status_get`` until ``status`` is
    ``success``, then ``workbookexports_result_get`` for the document.
    """
    return client.workbookexports.start(workbook_id)


@mcp.tool(
    name="workbookexports_status_get",
    annotations={**RO, "title": "Get DataLens workbook export status"},
)
def status_get(
    export_id: ExportID, client: DataLensClient = Depends(datalens_client)
) -> WorkbookExportStatus:
    """How far an export is: ``pending``, ``success`` or ``error``, and the progress in percent.

    ``notifications`` holds what the export has to say about an entry: id, level, message.
    """
    return client.workbookexports.status_get(export_id)


@mcp.tool(
    name="workbookexports_result_get",
    annotations={**RO, "title": "Get DataLens workbook export result"},
)
def result_get(
    export_id: ExportID, client: DataLensClient = Depends(datalens_client)
) -> WorkbookExport:
    """The exported workbook: every entry it holds, as one document.

    ``data`` is what ``workbookimports_start`` takes. An export that is not over, or was
    cancelled, answers 409 Conflict.
    """
    return client.workbookexports.result_get(export_id)


@mcp.tool(
    name="workbookexports_cancel",
    annotations={**WRITE_IDEMPOTENT, "title": "Cancel DataLens workbook export"},
)
def cancel(
    export_id: ExportID, client: DataLensClient = Depends(datalens_client)
) -> WorkbookExportCancelled:
    """Stop an export; cancelling one that is over, or twice, answers the same."""
    return client.workbookexports.cancel(export_id)
