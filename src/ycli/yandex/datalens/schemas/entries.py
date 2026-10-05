# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class GetEntriesRelationsArgs(RequestBody):
    entry_ids: list[str] = Field(
        ..., alias="entryIds", description="ID of the entries to get relations for."
    )
    link_direction: Literal["from", "to"] | str | None = Field(
        default=None,
        alias="linkDirection",
        description="The direction of the link relatively to the original entry:\n- `from` — entries the original entry links to, its direct dependencies\n- `to` — entries that link to the original entry, its direct dependents",
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in the response.",
    )
    limit: float | None = Field(default=None, description="Maximum number of results to return.")
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for retrieving the next page of results.",
    )
    scope: shared.EntryScope | None = None


class RenameEntryResultEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="ID of the renamed entry.")
    key: str = Field(..., description="Updated key of the entry.")
    scope: shared.EntryScope
    type: str = Field(..., description="Type of the renamed entry.")
    updated_at: str = Field(
        ..., alias="updatedAt", description="Date and time when the entry was renamed."
    )
    updated_by: str = Field(
        ..., alias="updatedBy", description="ID of the user who renamed the entry."
    )


class RenameEntryResult(RootModel[list[RenameEntryResultEntry]]):
    root: list[RenameEntryResultEntry]


class RenameEntryArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId", description="ID of the entry to rename.")
    name: str = Field(..., description="New name of the entry.")


class GetEntriesPermissionsArgs(RequestBody):
    entry_ids: list[str] = Field(
        ...,
        alias="entryIds",
        description="IDs of the entries to check permissions for.",
    )


class GetRevisionsArgs(RequestBody):
    entry_id: str = Field(
        ..., alias="entryId", description="Unique identifier of the DataLens entry."
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Number of revisions per page.",
        ge=1,
        le=1000,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for retrieving the next page of revisions.",
    )
    rev_ids: list[str] | None = Field(
        default=None,
        alias="revIds",
        description="IDs of revisions to return.",
        max_length=1000,
        min_length=1,
    )


class GetEntriesRelationsEntryPermissions(APIModel):
    """Basic permissions for the entry."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetEntriesRelationsEntryFullPermissions(APIModel):
    """Full permissions for the entry."""

    list_access_bindings: bool = Field(
        ...,
        alias="listAccessBindings",
        description="Permission to list access bindings.",
    )
    update_access_bindings: bool = Field(
        ...,
        alias="updateAccessBindings",
        description="Permission to update access bindings.",
    )
    limited_view: bool = Field(
        ..., alias="limitedView", description="Permission for limited viewing."
    )
    view: bool = Field(..., description="Permission to view.")
    update: bool = Field(..., description="Permission to update.")
    copy_: bool = Field(..., alias="copy", description="Permission to copy.")
    move: bool = Field(..., description="Permission to move.")
    delete: bool = Field(..., description="Permission to delete.")
    create_entry_binding: bool = Field(
        ...,
        alias="createEntryBinding",
        description="Permission to create entry binding.",
    )
    create_limited_entry_binding: bool = Field(
        ...,
        alias="createLimitedEntryBinding",
        description="Permission to create limited entry binding.",
    )


class GetEntriesPermissionsResultValueVariant1Permissions(APIModel):
    """Permissions for the entry."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetEntriesPermissionsResultValueVariant2(APIModel):
    error: Literal["NOT_FOUND"] = Field(..., description="Error code indicating a missing entry.")


class GetRevisionsResultEntriesItem(APIModel):
    rev_id: str = Field(..., alias="revId", description="Unique identifier of the revision.")
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="Date and time when the revision was last updated.",
    )
    updated_by: str = Field(
        ...,
        alias="updatedBy",
        description="ID of the user who last updated the revision.",
    )
    is_saved: bool = Field(
        ..., alias="isSaved", description="Whether this is the latest saved revision."
    )
    is_published: bool = Field(
        ..., alias="isPublished", description="Whether this is the published revision."
    )


class GetEntriesRelationsEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    scope: shared.EntryScope
    type: str = Field(
        ...,
        description="Specified type of the entry from scope (e.g. type of the connection or visualization type for charts).",
    )
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    public: bool = Field(..., description="Indicates if the entry is public.")
    tenant_id: str | None = Field(..., alias="tenantId", description="ID of the DataLens tenant.")
    workbook_id: str | None = Field(
        ..., alias="workbookId", description="ID of the workbook the entry belongs to."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection the entry belongs to.",
    )
    is_locked: bool | None = Field(
        default=None, alias="isLocked", description="Indicates if the entry is locked."
    )
    permissions: GetEntriesRelationsEntryPermissions | None = None
    full_permissions: GetEntriesRelationsEntryFullPermissions | None = Field(
        default=None, alias="fullPermissions"
    )


class GetEntriesRelationsResult(APIModel):
    relations: list[GetEntriesRelationsEntry] = Field(..., description="List of related entries.")
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for retrieving the next page of results.",
    )


class GetRevisionsResult(APIModel):
    entries: list[GetRevisionsResultEntriesItem]
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for retrieving the next page of revisions.",
    )


class GetEntriesPermissionsResultValueVariant1(APIModel):
    permissions: GetEntriesPermissionsResultValueVariant1Permissions


class GetEntriesPermissionsResult(
    RootModel[
        dict[
            str, GetEntriesPermissionsResultValueVariant1 | GetEntriesPermissionsResultValueVariant2
        ]
    ]
):
    root: dict[
        str, GetEntriesPermissionsResultValueVariant1 | GetEntriesPermissionsResultValueVariant2
    ]
