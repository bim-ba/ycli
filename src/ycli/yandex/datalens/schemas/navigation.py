# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class GetEntriesV2ResultEntriesItemPermissions(APIModel):
    """Permissions for the entry."""

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


class GetEntriesV2ArgsOrderBy(APIModel):
    """Entry sorting configuration."""

    field: Literal["createdAt", "name"] | str | None = Field(
        default=None, description="Field used to sort entries: creation date or name."
    )
    direction: Literal["desc", "asc"] | str | None = Field(
        default=None, description="Entry sort direction."
    )


class GetEntriesV2ArgsFilters(APIModel):
    """Entry filters."""

    name: str | None = Field(default=None, description="Name used to filter entries.")


class ListDirectoryBreadCrumbPermissions(APIModel):
    """Permissions for the breadcrumb item."""

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


class ListDirectoryEntryPermissions(APIModel):
    """Permissions for the entry."""

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


class ListDirectoryArgsOrderBy(APIModel):
    """Sorting configuration."""

    field: Literal["createdAt", "name"] | str | None = Field(
        default=None, description="Field used to sort entries: creation date or name."
    )
    direction: Literal["desc", "asc"] | str | None = Field(
        default=None, description="Entry sort direction."
    )


class ListDirectoryArgsFilters(APIModel):
    """Filtering configuration."""

    name: str | None = Field(default=None, description="Name used to filter entries.")


class GetEntriesV2Args(RequestBody):
    ids: list[str] | None = Field(default=None, description="IDs of entries to return.")
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
        default=None, description="Scopes used to filter entries."
    )
    type: str | list[str] | None = Field(
        default=None, description="Entry type or types to filter by."
    )
    created_by: list[str] | None = Field(
        default=None,
        alias="createdBy",
        description="IDs of entry creators to filter by.",
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
    title: str | None = Field(default=None, description="Title of the breadcrumb item.")
    path: str | None = Field(default=None, description="Path of the breadcrumb item.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Entry ID of the breadcrumb item."
    )
    is_locked: bool | None = Field(
        default=None, alias="isLocked", description="Indicates if the item is locked."
    )
    permissions: ListDirectoryBreadCrumbPermissions | None = None


class ListDirectoryEntry(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    key: str | None = Field(default=None, description="Key identifier of the entry.")
    scope: shared.EntryScope | None = None
    type: str | None = Field(
        default=None, description="Type of the entry (e.g., dash, dataset, connection)."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Creator of the entry."
    )
    updated_by: str | None = Field(
        default=None, alias="updatedBy", description="Last updater of the entry."
    )
    saved_id: str | None = Field(default=None, alias="savedId", description="Saved version ID.")
    published_id: str | None = Field(
        default=None, alias="publishedId", description="Published version ID."
    )
    hidden: bool | None = Field(default=None, description="Indicates if the entry is hidden.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the entry belongs to.",
    )
    workbook_title: str | None = Field(
        default=None, alias="workbookTitle", description="Workbook name."
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection the entry belongs to.",
    )
    collection_title: str | None = Field(
        default=None, alias="collectionTitle", description="Collection name."
    )
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Indicates if the entry is marked as favorite.",
    )
    is_locked: bool | None = Field(
        default=None, alias="isLocked", description="Indicates if the entry is locked."
    )
    permissions: ListDirectoryEntryPermissions | None = None
    name: str | None = Field(default=None, description="Name of the entry.")


class ListDirectoryResult(APIModel):
    has_next_page: bool | None = Field(
        default=None,
        alias="hasNextPage",
        description="Indicates if there are more pages.",
    )
    bread_crumbs: list[ListDirectoryBreadCrumb] | None = Field(
        default=None,
        alias="breadCrumbs",
        description="Navigation breadcrumbs for the current path.",
    )
    entries: list[ListDirectoryEntry] | None = Field(
        default=None, description="List of directory entries."
    )


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
    page: int | float | None = Field(default=None, description="Page number for pagination.")
    page_size: int | float | None = Field(
        default=None, alias="pageSize", description="Number of entries per page."
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in response.",
    )


class GetEntriesV2ResultEntriesItem(APIModel):
    is_locked: bool | None = Field(
        default=None,
        alias="isLocked",
        description="Indicates that the entry is locked.",
    )
    entry_id: str | None = Field(
        default=None,
        alias="entryId",
        description="Unique identifier of the locked entry.",
    )
    scope: shared.EntryScope | None = None
    type: str | None = Field(default=None, description="Type of the locked entry.")
    name: str | None = Field(default=None, description="Name of the entry.")
    key: str | None = Field(default=None, description="Key of the entry.")
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the entry."
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the entry was created.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the entry was last updated.",
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the entry.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the entry.",
    )
    saved_id: str | None = Field(
        default=None, alias="savedId", description="ID of the saved entry revision."
    )
    published_id: str | None = Field(
        default=None,
        alias="publishedId",
        description="ID of the published entry revision.",
    )
    hidden: bool | None = Field(default=None, description="Whether the entry is hidden.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook containing the entry.",
    )
    workbook_title: str | None = Field(
        default=None,
        alias="workbookTitle",
        description="Title of the workbook containing the entry.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection containing the entry.",
    )
    collection_title: str | None = Field(
        default=None,
        alias="collectionTitle",
        description="Title of the collection containing the entry.",
    )
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Whether the entry is marked as a favorite.",
    )
    permissions: GetEntriesV2ResultEntriesItemPermissions | None = None
    links: dict[str, Any] | None = Field(
        default=None, description="Links associated with the entry."
    )
    data: dict[str, Any] | None = Field(default=None, description="Data stored in the entry.")


class GetEntriesV2Result(APIModel):
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of entries.",
    )
    entries: list[GetEntriesV2ResultEntriesItem] | None = Field(
        default=None, description="Entries matching the request."
    )
