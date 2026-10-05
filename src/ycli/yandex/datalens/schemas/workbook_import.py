# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class StartWorkbookImportResult(APIModel):
    import_id: str = Field(..., alias="importId", description="ID of the started workbook import.")
    workbook_id: str = Field(
        ..., alias="workbookId", description="ID of the workbook created by the import."
    )


class StartWorkbookImportArgs(RequestBody):
    data: dict[str, Any] = Field(..., description="Serialized workbook export data to import.")
    title: str = Field(..., description="Title of the imported workbook.")
    description: str | None = Field(
        default=None, description="Description of the imported workbook."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection in which to create the imported workbook.",
    )


class GetWorkbookImportStatusResult(APIModel):
    import_id: str = Field(..., alias="importId", description="ID of the workbook import.")
    workbook_id: str = Field(..., alias="workbookId", description="ID of the imported workbook.")
    status: shared.WorkbookTransferProcessStatus
    progress: float = Field(..., description="Workbook import progress percentage.")
    notifications: list[shared.WorkbookTransferNotification] | None = Field(
        ..., description="Notifications generated during the workbook import."
    )


class GetWorkbookImportStatusArgs(RequestBody):
    import_id: str = Field(
        ...,
        alias="importId",
        description="ID of the workbook import whose status to retrieve.",
    )
