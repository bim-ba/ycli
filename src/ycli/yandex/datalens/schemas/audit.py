# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class AuditEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry")
    key: str | None = Field(..., description="Entry key identifier")
    is_deleted: bool = Field(
        ..., alias="isDeleted", description="Flag indicating if the entry is deleted"
    )
    workbook_id: str | None = Field(
        ..., alias="workbookId", description="ID of the associated workbook"
    )
    collection_id: str | None = Field(
        ..., alias="collectionId", description="ID of the associated collection"
    )
    parent_folder_id: str | None = Field(
        ..., alias="parentFolderId", description="ID of the associated folder"
    )
    scope: shared.EntryScope
    type: str | None = Field(..., description="Type of the entry")
    updated_at: str = Field(..., alias="updatedAt", description="Timestamp of the last update")
    user_id: str = Field(..., alias="userId", description="ID of the user who made the change")


class GetAuditEntriesUpdatesResult(APIModel):
    entries: list[AuditEntry] = Field(..., description="Entries updated in the requested period.")
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of results",
    )


class GetAuditEntriesUpdatesArgs(RequestBody):
    from_: AwareDatetime = Field(
        ..., alias="from", description="Start date for filtering entries by updatedAt"
    )
    to: AwareDatetime | None = Field(
        default=None, description="End date for filtering entries by updatedAt"
    )
    limit: float | None = Field(default=None, description="Maximum number of entries to return")
    page_token: str | None = Field(
        default=None, alias="pageToken", description="Token for pagination"
    )


class Permissions(APIModel):
    """Permissions granted to the user for the entry."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetAuditEntryPermissionsForUserResult(APIModel):
    permissions: Permissions = Field(
        ..., description="Permissions granted to the user for the entry."
    )


class GetAuditEntryPermissionsForUserResultModel(APIModel):
    error: Literal["NOT_FOUND"] = Field(..., description="Error code indicating a missing entry.")


class GetAuditEntryPermissionsForUserResultModel1(
    RootModel[
        dict[
            str, GetAuditEntryPermissionsForUserResult | GetAuditEntryPermissionsForUserResultModel
        ]
    ]
):
    root: dict[
        str, GetAuditEntryPermissionsForUserResult | GetAuditEntryPermissionsForUserResultModel
    ]


class GetAuditEntryPermissionsForUserArgs(RequestBody):
    entry_ids: list[str] = Field(
        ...,
        alias="entryIds",
        description="IDs of the entries to check permissions for.",
    )
    user_id: str = Field(
        ...,
        alias="userId",
        description="ID of the user whose permissions should be returned.",
    )
