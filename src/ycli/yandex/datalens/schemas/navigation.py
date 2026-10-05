# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class Type(RootModel[list[str]]):
    root: list[str] = Field(
        ...,
        description="Entry type or types to filter by.",
        max_length=10,
        min_length=1,
    )


class GetEntriesV2ResultEntriesItemVariant1(APIModel):
    is_locked: Literal[True] = Field(
        ..., alias="isLocked", description="Indicates that the entry is locked."
    )
    entry_id: str = Field(
        ..., alias="entryId", description="Unique identifier of the locked entry."
    )
    scope: shared.EntryScope
    type: str = Field(..., description="Type of the locked entry.")
    name: str = Field(..., description="Name of the entry.")


class GetEntriesV2ResultEntriesItemVariant2Permissions(APIModel):
    """Permissions for the entry."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetEntriesV2ArgsOrderBy(APIModel):
    """Entry sorting configuration."""

    field: Literal["createdAt", "name"] | str = Field(
        ..., description="Field used to sort entries: creation date or name."
    )
    direction: Literal["desc", "asc"] | str = Field(..., description="Entry sort direction.")


class GetEntriesV2ArgsFilters(APIModel):
    """Entry filters."""

    name: str | None = Field(default=None, description="Name used to filter entries.")


class ListDirectoryBreadCrumbPermissions(APIModel):
    """Permissions for the breadcrumb item."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class ListDirectoryEntryPermissions(APIModel):
    """Permissions for the entry."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class ListDirectoryArgsOrderBy(APIModel):
    """Sorting configuration."""

    field: Literal["createdAt", "name"] | str = Field(
        ..., description="Field used to sort entries: creation date or name."
    )
    direction: Literal["desc", "asc"] | str = Field(..., description="Entry sort direction.")


class ListDirectoryArgsFilters(APIModel):
    """Filtering configuration."""

    name: str | None = Field(default=None, description="Name used to filter entries.")


class GetEntriesV2Args(RequestBody):
    ids: list[str] | None = Field(
        default=None, description="IDs of entries to return.", max_length=1000
    )
    scope: (
        Literal[
            "dash",
            "report",
            "widget",
            "dataset",
            "folder",
            "connection",
            "compute",
            "artifact",
            "sql_query",
        ]
        | str
        | None
    ) = Field(default=None, description="Scope used to filter entries.")
    scopes: list[shared.EntryScope] | None = Field(
        default=None, description="Scopes used to filter entries.", min_length=1
    )
    type: str | Type | None = Field(default=None, description="Entry type or types to filter by.")
    created_by: list[str] | None = Field(
        default=None,
        alias="createdBy",
        description="IDs of entry creators to filter by.",
        max_length=1000,
    )
    order_by: GetEntriesV2ArgsOrderBy | None = Field(default=None, alias="orderBy")
    exclude_locked: bool | None = Field(
        default=None,
        alias="excludeLocked",
        description="Whether to exclude locked entries.",
    )
    include_links: bool | None = Field(
        default=None,
        alias="includeLinks",
        description="Whether to include entry links.",
    )
    filters: GetEntriesV2ArgsFilters | None = None
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of entries to return.",
        ge=1,
        le=200,
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Whether to include permission information.",
    )
    ignore_workbook_entries: bool | None = Field(
        default=None,
        alias="ignoreWorkbookEntries",
        description="Whether to exclude entries that belong to workbooks.",
    )
    ignore_shared_entries: bool | None = Field(
        default=None,
        alias="ignoreSharedEntries",
        description="Whether to exclude shared entries.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of entries.",
    )
    include_data: bool | None = Field(
        default=None, alias="includeData", description="Whether to include entry data."
    )


class ListDirectoryBreadCrumb(APIModel):
    title: str = Field(..., description="Title of the breadcrumb item.")
    path: str = Field(..., description="Path of the breadcrumb item.")
    entry_id: str = Field(..., alias="entryId", description="Entry ID of the breadcrumb item.")
    is_locked: bool = Field(..., alias="isLocked", description="Indicates if the item is locked.")
    permissions: ListDirectoryBreadCrumbPermissions


class ListDirectoryEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str = Field(..., description="Key identifier of the entry.")
    scope: shared.EntryScope
    type: str = Field(..., description="Type of the entry (e.g., dash, dataset, connection).")
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    created_by: str = Field(..., alias="createdBy", description="Creator of the entry.")
    updated_by: str = Field(..., alias="updatedBy", description="Last updater of the entry.")
    saved_id: str = Field(..., alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published version ID.")
    hidden: bool = Field(..., description="Indicates if the entry is hidden.")
    workbook_id: str = Field(
        ..., alias="workbookId", description="ID of the workbook the entry belongs to."
    )
    workbook_title: str | None = Field(
        default=None, alias="workbookTitle", description="Workbook name."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection the entry belongs to.",
    )
    collection_title: str | None = Field(
        default=None, alias="collectionTitle", description="Collection name."
    )
    is_favorite: bool = Field(
        ...,
        alias="isFavorite",
        description="Indicates if the entry is marked as favorite.",
    )
    is_locked: bool = Field(..., alias="isLocked", description="Indicates if the entry is locked.")
    permissions: ListDirectoryEntryPermissions | None = None
    name: str = Field(..., description="Name of the entry.")


class ListDirectoryResult(APIModel):
    has_next_page: bool = Field(
        ..., alias="hasNextPage", description="Indicates if there are more pages."
    )
    bread_crumbs: list[ListDirectoryBreadCrumb] = Field(
        ...,
        alias="breadCrumbs",
        description="Navigation breadcrumbs for the current path.",
    )
    entries: list[ListDirectoryEntry] = Field(..., description="List of directory entries.")


class ListDirectoryArgs(RequestBody):
    path: str | None = Field(default=None, description="Directory path to list entries from.")
    scope: shared.EntryScope | list[shared.EntryScope] | None = Field(
        default=None, description="Entry scope or scopes to filter by."
    )
    created_by: str | list[str] | None = Field(
        default=None, alias="createdBy", description="Filter entries by creator."
    )
    order_by: ListDirectoryArgsOrderBy | None = Field(default=None, alias="orderBy")
    filters: ListDirectoryArgsFilters | None = None
    page: float | None = Field(default=None, description="Page number for pagination.")
    page_size: float | None = Field(
        default=None, alias="pageSize", description="Number of entries per page."
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in response.",
    )


class GetEntriesV2ResultEntriesItemVariant2(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    key: str = Field(..., description="Key of the entry.")
    scope: shared.EntryScope
    type: str = Field(..., description="Type of the entry.")
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    created_at: str = Field(
        ..., alias="createdAt", description="Date and time when the entry was created."
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="Date and time when the entry was last updated.",
    )
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the entry."
    )
    updated_by: str = Field(
        ..., alias="updatedBy", description="ID of the user who last updated the entry."
    )
    saved_id: str = Field(..., alias="savedId", description="ID of the saved entry revision.")
    published_id: str | None = Field(
        ..., alias="publishedId", description="ID of the published entry revision."
    )
    hidden: bool = Field(..., description="Whether the entry is hidden.")
    workbook_id: str | None = Field(
        ..., alias="workbookId", description="ID of the workbook containing the entry."
    )
    workbook_title: str | None = Field(
        default=None,
        alias="workbookTitle",
        description="Title of the workbook containing the entry.",
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection containing the entry.",
    )
    collection_title: str | None = Field(
        default=None,
        alias="collectionTitle",
        description="Title of the collection containing the entry.",
    )
    is_favorite: bool = Field(
        ...,
        alias="isFavorite",
        description="Whether the entry is marked as a favorite.",
    )
    is_locked: Literal[False] | None = Field(
        default=None,
        alias="isLocked",
        description="Indicates that the entry is not locked.",
    )
    permissions: GetEntriesV2ResultEntriesItemVariant2Permissions | None = None
    links: dict[str, Any] | None = Field(..., description="Links associated with the entry.")
    data: dict[str, Any] | None = Field(default=None, description="Data stored in the entry.")
    name: str = Field(..., description="Name of the entry.")


class GetEntriesV2Result(APIModel):
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of entries.",
    )
    entries: list[GetEntriesV2ResultEntriesItemVariant1 | GetEntriesV2ResultEntriesItemVariant2] = (
        Field(..., description="Entries matching the request.")
    )
