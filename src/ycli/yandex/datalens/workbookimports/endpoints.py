"""DataLens workbook import operations, declared once (sans-IO).

Examples:
    >>> status_get("imp1").body
    {'importId': 'imp1'}
"""

from typing import Any

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.schemas.workbook_import import (
    GetWorkbookImportStatusArgs,
    StartWorkbookImportArgs,
)
from ycli.yandex.datalens.workbookimports.models import (
    WorkbookImportStarted,
    WorkbookImportStatus,
)


def start(
    data: dict[str, Any], *, title: str, collection_id: str | None, description: str | None
) -> Endpoint[WorkbookImportStarted]:
    body = StartWorkbookImportArgs(
        data=data, title=title, collectionId=collection_id, description=description
    )
    return RPC("startWorkbookImport", WorkbookImportStarted, json=body, effect=Effect.WRITE)


def status_get(import_id: str) -> Endpoint[WorkbookImportStatus]:
    body = GetWorkbookImportStatusArgs(importId=import_id)
    return RPC("getWorkbookImportStatus", WorkbookImportStatus, json=body, effect=Effect.READ)
