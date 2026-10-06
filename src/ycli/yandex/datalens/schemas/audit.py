# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, RootModel

from ycli.yandex.models import APIModel, NoDropNull, RequestBody

from . import shared


class AuditEntry(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry"
    )
    key: Annotated[str | None, NoDropNull()] = Field(
        default=None, description="Entry key identifier"
    )
    is_deleted: bool | None = Field(
        default=None,
        alias="isDeleted",
        description="Flag indicating if the entry is deleted",
    )
    workbook_id: Annotated[str | None, NoDropNull()] = Field(
        default=None, alias="workbookId", description="ID of the associated workbook"
    )
    collection_id: Annotated[str | None, NoDropNull()] = Field(
        default=None,
        alias="collectionId",
        description="ID of the associated collection",
    )
    parent_folder_id: Annotated[str | None, NoDropNull()] = Field(
        default=None, alias="parentFolderId", description="ID of the associated folder"
    )
    scope: shared.EntryScope | None = None
    type: Annotated[str | None, NoDropNull()] = Field(default=None, description="Type of the entry")
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Timestamp of the last update"
    )
    user_id: str | None = Field(
        default=None, alias="userId", description="ID of the user who made the change"
    )


class GetAuditEntriesUpdatesResult(APIModel):
    entries: list[AuditEntry] | None = Field(
        default=None, description="Entries updated in the requested period."
    )
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
    limit: int | float | None = Field(
        default=None, description="Maximum number of entries to return"
    )
    page_token: str | None = Field(
        default=None, alias="pageToken", description="Token for pagination"
    )


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


class GetAuditEntryPermissionsForUserResultValuePermissions(APIModel):
    """Permissions granted to the user for the entry."""

    execute: bool | None = Field(
        default=None, description="Indicates if there are permissions to execute."
    )
    read: bool | None = Field(
        default=None, description="Indicates if there are permissions to read."
    )
    edit: bool | None = Field(
        default=None, description="Indicates if there are permissions to edit."
    )
    admin: bool | None = Field(
        default=None, description="Indicates if there are permissions for admin."
    )


class GetAuditEntryPermissionsForUserResultValue(APIModel):
    permissions: GetAuditEntryPermissionsForUserResultValuePermissions | None = None
    error: Literal["NOT_FOUND"] | str | None = Field(
        default=None, description="Error code indicating a missing entry."
    )


class GetAuditEntryPermissionsForUserResult(
    RootModel[dict[str, GetAuditEntryPermissionsForUserResultValue]], hide_input_in_errors=True
):
    root: dict[str, GetAuditEntryPermissionsForUserResultValue]
