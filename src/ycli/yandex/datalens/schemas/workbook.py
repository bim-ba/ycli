# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class Meta(APIModel):
    """Metadata associated with the workbook."""

    import_id: str | None = Field(
        default=None,
        alias="importId",
        description="ID of the workbook import operation.",
    )


class CreateWorkbookResult(APIModel):
    workbook_id: str = Field(
        ..., alias="workbookId", description="Unique identifier of the workbook."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection the workbook belongs to.",
    )
    title: str = Field(..., description="Title of the workbook.")
    description: str | None = Field(..., description="Description of the workbook.")
    tenant_id: str = Field(..., alias="tenantId", description="ID of the DataLens tenant.")
    meta: Meta = Field(..., description="Metadata associated with the workbook.")
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the workbook."
    )
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    updated_by: str = Field(
        ...,
        alias="updatedBy",
        description="ID of the user who last updated the workbook.",
    )
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    status: Literal["creating", "deleting", "active", "deleted"] | str | None = Field(
        default=None, description="Status of the workbook."
    )
    operation: shared.DatalensOperation


class CreateWorkbookArgs(RequestBody):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection in which to create the workbook.",
    )
    title: str = Field(..., description="Title of the workbook.")
    description: str | None = Field(default=None, description="Description of the workbook.")


class Workbook(APIModel):
    workbook_id: str = Field(
        ..., alias="workbookId", description="Unique identifier of the workbook."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection the workbook belongs to.",
    )
    title: str = Field(..., description="Title of the workbook.")
    description: str | None = Field(..., description="Description of the workbook.")
    tenant_id: str = Field(..., alias="tenantId", description="ID of the DataLens tenant.")
    meta: Meta = Field(..., description="Metadata associated with the workbook.")
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the workbook."
    )
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    updated_by: str = Field(
        ...,
        alias="updatedBy",
        description="ID of the user who last updated the workbook.",
    )
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    status: Literal["creating", "deleting", "active", "deleted"] | str | None = Field(
        default=None, description="Status of the workbook."
    )


class DeleteWorkbookArgs(RequestBody):
    workbook_id: str = Field(..., alias="workbookId", description="ID of the workbook to delete.")


class DeleteWorkbooksArgs(RequestBody):
    workbook_ids: list[str] = Field(
        ..., alias="workbookIds", description="IDs of the workbooks to delete."
    )


class Permissions(APIModel):
    """Permissions for the workbook."""

    list_access_bindings: bool = Field(
        ...,
        alias="listAccessBindings",
        description="Indicates if access bindings for the workbook can be listed.",
    )
    update_access_bindings: bool = Field(
        ...,
        alias="updateAccessBindings",
        description="Indicates if access bindings for the workbook can be updated.",
    )
    limited_view: bool = Field(
        ...,
        alias="limitedView",
        description="Indicates if the workbook can be viewed with limited access.",
    )
    view: bool = Field(..., description="Indicates if the workbook can be viewed.")
    update: bool = Field(..., description="Indicates if the workbook can be updated.")
    copy_: bool = Field(..., alias="copy", description="Indicates if the workbook can be copied.")
    move: bool = Field(..., description="Indicates if the workbook can be moved.")
    publish: bool = Field(..., description="Indicates if entries in the workbook can be published.")
    embed: bool = Field(..., description="Indicates if entries in the workbook can be embedded.")
    delete: bool = Field(..., description="Indicates if the workbook can be deleted.")


class GetWorkbookResult(APIModel):
    workbook_id: str = Field(
        ..., alias="workbookId", description="Unique identifier of the workbook."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection the workbook belongs to.",
    )
    title: str = Field(..., description="Title of the workbook.")
    description: str | None = Field(..., description="Description of the workbook.")
    tenant_id: str = Field(..., alias="tenantId", description="ID of the DataLens tenant.")
    meta: Meta = Field(..., description="Metadata associated with the workbook.")
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the workbook."
    )
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    updated_by: str = Field(
        ...,
        alias="updatedBy",
        description="ID of the user who last updated the workbook.",
    )
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    status: Literal["creating", "deleting", "active", "deleted"] | str | None = Field(
        default=None, description="Status of the workbook."
    )
    permissions: Permissions = Field(..., description="Permissions for the workbook.")


class GetWorkbookArgs(RequestBody):
    workbook_id: str = Field(..., alias="workbookId", description="ID of the workbook to retrieve.")
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in the response.",
    )


class WorkbookModel(APIModel):
    workbook_id: str = Field(
        ..., alias="workbookId", description="Unique identifier of the workbook."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection the workbook belongs to.",
    )
    title: str = Field(..., description="Title of the workbook.")
    description: str | None = Field(..., description="Description of the workbook.")
    tenant_id: str = Field(..., alias="tenantId", description="ID of the DataLens tenant.")
    meta: Meta = Field(..., description="Metadata associated with the workbook.")
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the workbook."
    )
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    updated_by: str = Field(
        ...,
        alias="updatedBy",
        description="ID of the user who last updated the workbook.",
    )
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    status: Literal["creating", "deleting", "active", "deleted"] | str | None = Field(
        default=None, description="Status of the workbook."
    )
    permissions: Permissions | None = Field(
        default=None, description="Permissions for the workbook."
    )


class GetWorkbooksListResult(APIModel):
    workbooks: list[WorkbookModel] = Field(..., description="List of workbooks.")
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for retrieving the next page of results.",
    )


class GetWorkbooksListArgs(RequestBody):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="Filter workbooks by collection ID.",
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in the response.",
    )
    filter_string: str | None = Field(
        default=None, alias="filterString", description="Filter workbooks by title."
    )
    page: float | None = Field(default=None, description="Page number for pagination.")
    page_size: float | None = Field(
        default=None, alias="pageSize", description="Number of workbooks per page."
    )
    order_field: Literal["title", "createdAt", "updatedAt"] | str | None = Field(
        default=None, alias="orderField", description="Field to order workbooks by."
    )
    order_direction: Literal["asc", "desc"] | str | None = Field(
        default=None, alias="orderDirection", description="Workbook sorting direction."
    )
    only_my: bool | None = Field(
        default=None,
        alias="onlyMy",
        description="Return only workbooks created by the current user.",
    )


class GetWorkbooksByIdsArgs(RequestBody):
    workbook_ids: list[str] = Field(
        ...,
        alias="workbookIds",
        description="IDs of the workbooks to retrieve.",
        max_length=1000,
        min_length=1,
    )


class MoveWorkbookArgs(RequestBody):
    workbook_id: str = Field(..., alias="workbookId", description="ID of the workbook to move.")
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection to move the workbook to.",
    )
    title: str | None = Field(default=None, description="New title of the workbook.")


class MoveWorkbooksArgs(RequestBody):
    workbook_ids: list[str] = Field(
        ..., alias="workbookIds", description="IDs of the workbooks to move."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection to move the workbooks to.",
    )


class UpdateWorkbookArgs(RequestBody):
    workbook_id: str = Field(..., alias="workbookId", description="ID of the workbook to update.")
    title: str | None = Field(default=None, description="New title of the workbook.")
    description: str | None = Field(default=None, description="New description of the workbook.")


class PermissionsModel(APIModel):
    """Permissions for the entry."""

    execute: bool = Field(..., description="Indicates if there are permissions to execute.")
    read: bool = Field(..., description="Indicates if there are permissions to read.")
    edit: bool = Field(..., description="Indicates if there are permissions to edit.")
    admin: bool = Field(..., description="Indicates if there are permissions for admin.")


class GetWorkbookEntriesEntry(APIModel):
    entry_id: str = Field(..., alias="entryId", description="Unique identifier of the entry.")
    scope: shared.EntryScope
    type: str = Field(..., description="Entity type of the entry.")
    key: str | None = Field(..., description="Key identifier of the entry.")
    display_key: str | None = Field(
        ..., alias="displayKey", description="Display key of the entry."
    )
    created_by: str = Field(
        ..., alias="createdBy", description="ID of the user who created the entry."
    )
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp.")
    updated_by: str = Field(
        ..., alias="updatedBy", description="ID of the user who last updated the entry."
    )
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp.")
    saved_id: str | None = Field(..., alias="savedId", description="Saved revision ID.")
    published_id: str | None = Field(..., alias="publishedId", description="Published revision ID.")
    rev_id: str = Field(..., alias="revId", description="Current revision ID.")
    meta: dict[str, Any] | None = Field(..., description="Metadata associated with the entry.")
    hidden: bool | None = Field(..., description="Indicates if the entry is hidden.")
    workbook_id: str | None = Field(
        ..., alias="workbookId", description="ID of the workbook the entry belongs to."
    )
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection the entry belongs to.",
    )
    tenant_id: str | None = Field(..., alias="tenantId", description="ID of the DataLens tenant.")
    is_favorite: bool = Field(
        ...,
        alias="isFavorite",
        description="Indicates if the entry is marked as favorite.",
    )
    is_locked: bool = Field(..., alias="isLocked", description="Indicates if the entry is locked.")
    permissions: PermissionsModel | None = Field(
        default=None, description="Permissions for the entry."
    )
    mirrored: bool | None = Field(..., description="Indicates if the entry is mirrored.")


class GetWorkbookEntriesResult(APIModel):
    entries: list[GetWorkbookEntriesEntry] = Field(..., description="List of workbook entries.")
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for retrieving the next page of results.",
    )


class OrderBy(APIModel):
    """Sorting configuration."""

    field: Literal["name", "scope", "createdAt", "updatedAt"] | str = Field(
        ..., description="Field to order workbook entries by."
    )
    direction: Literal["asc", "desc"] | str = Field(
        ..., description="Workbook entry sorting direction."
    )


class Filters(APIModel):
    """Filtering configuration."""

    name: str = Field(..., description="Filter entries by name.")


class GetWorkbookEntriesArgs(RequestBody):
    workbook_id: str = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook whose entries to retrieve.",
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in the response.",
    )
    page: float | None = Field(default=None, description="Page number for pagination.")
    page_size: float | None = Field(
        default=None, alias="pageSize", description="Number of entries per page."
    )
    only_my: bool | None = Field(
        default=None,
        alias="onlyMy",
        description="Return only entries created by the current user.",
    )
    created_by: str | None = Field(
        default=None, alias="createdBy", description="Filter entries by creator ID."
    )
    scope: shared.EntryScope | list[shared.EntryScope] | None = Field(
        default=None, description="Filter entries by scope."
    )
    order_by: OrderBy | None = Field(
        default=None, alias="orderBy", description="Sorting configuration."
    )
    filters: Filters | None = Field(default=None, description="Filtering configuration.")


class UpdateWorkbookAccessBindingsArgs(RequestBody):
    workbook_id: str = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook whose access bindings to update.",
    )
    deltas: list[shared.USAccessBindingDelta] = Field(
        ..., description="Access binding changes to apply."
    )


class ListWorkbookAccessBindingsArgs(RequestBody):
    workbook_id: str = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook whose access bindings to retrieve.",
    )
    get_inherited_bindings: bool | None = Field(
        default=None,
        alias="getInheritedBindings",
        description="Include access bindings inherited from parent resources.",
    )
    page_size: float | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of subjects to return.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for retrieving the next page of results.",
    )


class DeleteWorkbooksResponse(APIModel):
    workbooks: list[Workbook] = Field(..., description="Deleted workbooks.")


class GetWorkbooksByIdsResponse(RootModel[list[Workbook]]):
    root: list[Workbook]


class MoveWorkbooksResponse(APIModel):
    workbooks: list[Workbook] = Field(..., description="Moved workbooks.")
