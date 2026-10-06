# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class StartWorkbookExportResult(APIModel):
    export_id: str | None = Field(
        default=None, alias="exportId", description="ID of the started workbook export."
    )


class StartWorkbookExportArgs(RequestBody):
    workbook_id: str = Field(..., alias="workbookId", description="ID of the workbook to export.")


class GetWorkbookExportStatusResult(APIModel):
    export_id: str | None = Field(
        default=None, alias="exportId", description="ID of the workbook export."
    )
    status: shared.WorkbookTransferProcessStatus | None = None
    progress: int | float | None = Field(
        default=None, description="Workbook export progress percentage."
    )
    notifications: list[shared.WorkbookTransferNotification] | None = Field(
        default=None, description="Notifications generated during the workbook export."
    )


class GetWorkbookExportStatusArgs(RequestBody):
    export_id: str = Field(
        ...,
        alias="exportId",
        description="ID of the workbook export whose status to retrieve.",
    )


class GetWorkbookExportResultArgs(RequestBody):
    export_id: str = Field(
        ...,
        alias="exportId",
        description="ID of the workbook export whose result to retrieve.",
    )


class CancelWorkbookExportResult(APIModel):
    export_id: str | None = Field(
        default=None,
        alias="exportId",
        description="ID of the canceled workbook export.",
    )


class CancelWorkbookExportArgs(RequestBody):
    export_id: str = Field(
        ..., alias="exportId", description="ID of the workbook export to cancel."
    )


class GetWorkbookExportResultResultData(APIModel):
    export: dict[str, Any] | None = Field(
        default=None, description="Serialized workbook export data."
    )
    hash: str | None = Field(
        default=None, description="Hash of the serialized workbook export data."
    )


class GetWorkbookExportResultResult(APIModel):
    export_id: str | None = Field(
        default=None, alias="exportId", description="ID of the workbook export."
    )
    data: GetWorkbookExportResultResultData | None = None
    status: shared.WorkbookTransferProcessStatus | None = None
