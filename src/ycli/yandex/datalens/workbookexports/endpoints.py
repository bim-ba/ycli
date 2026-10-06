"""DataLens workbook export operations, declared once (sans-IO).

Examples:
    >>> start("wb1").body
    {'workbookId': 'wb1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.schemas.workbook_export import (
    CancelWorkbookExportArgs,
    GetWorkbookExportResultArgs,
    GetWorkbookExportStatusArgs,
    StartWorkbookExportArgs,
)
from ycli.yandex.datalens.workbookexports.models import (
    WorkbookExport,
    WorkbookExportCancelled,
    WorkbookExportStarted,
    WorkbookExportStatus,
)


def start(workbook_id: str) -> Endpoint[WorkbookExportStarted]:
    body = StartWorkbookExportArgs(workbookId=workbook_id)
    return RPC("startWorkbookExport", WorkbookExportStarted, json=body, effect=Effect.WRITE)


def status_get(export_id: str) -> Endpoint[WorkbookExportStatus]:
    body = GetWorkbookExportStatusArgs(exportId=export_id)
    return RPC("getWorkbookExportStatus", WorkbookExportStatus, json=body, effect=Effect.READ)


def result_get(export_id: str) -> Endpoint[WorkbookExport]:
    body = GetWorkbookExportResultArgs(exportId=export_id)
    return RPC("getWorkbookExportResult", WorkbookExport, json=body, effect=Effect.READ)


def cancel(export_id: str) -> Endpoint[WorkbookExportCancelled]:
    # Measured: cancelling again, or an export that is over, answers 200 the same.
    body = CancelWorkbookExportArgs(exportId=export_id)
    return RPC(
        "cancelWorkbookExport", WorkbookExportCancelled, json=body, effect=Effect.IDEMPOTENT_WRITE
    )
