# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class StartWorkbookExportResult(APIModel):
    export_id: str = Field(..., alias="exportId", description="ID of the started workbook export.")


class StartWorkbookExportArgs(RequestBody):
    workbook_id: str = Field(..., alias="workbookId", description="ID of the workbook to export.")


class GetWorkbookExportStatusResult(APIModel):
    export_id: str = Field(..., alias="exportId", description="ID of the workbook export.")
    status: shared.WorkbookTransferProcessStatus
    progress: float = Field(..., description="Workbook export progress percentage.")
    notifications: list[shared.WorkbookTransferNotification] | None = Field(
        default=None, description="Notifications generated during the workbook export."
    )


class GetWorkbookExportStatusArgs(RequestBody):
    export_id: str = Field(
        ...,
        alias="exportId",
        description="ID of the workbook export whose status to retrieve.",
    )


class Data(APIModel):
    export: dict[str, Any] = Field(..., description="Serialized workbook export data.")
    hash: str = Field(..., description="Hash of the serialized workbook export data.")


class GetWorkbookExportResultResult(APIModel):
    export_id: str = Field(..., alias="exportId", description="ID of the workbook export.")
    data: Data
    status: shared.WorkbookTransferProcessStatus


class GetWorkbookExportResultArgs(RequestBody):
    export_id: str = Field(
        ...,
        alias="exportId",
        description="ID of the workbook export whose result to retrieve.",
    )


class CancelWorkbookExportResult(APIModel):
    export_id: str = Field(..., alias="exportId", description="ID of the canceled workbook export.")


class CancelWorkbookExportArgs(RequestBody):
    export_id: str = Field(
        ..., alias="exportId", description="ID of the workbook export to cancel."
    )
