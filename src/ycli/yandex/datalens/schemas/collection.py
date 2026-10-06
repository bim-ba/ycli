# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class CreateCollectionArgs(RequestBody):
    title: str = Field(..., description="Title of the collection.")
    description: str | None = Field(default=None, description="Description of the collection.")
    parent_id: str | None = Field(
        ...,
        alias="parentId",
        description="ID of the parent collection in which to create the collection.",
    )


class Collection(APIModel):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="Unique identifier of the collection.",
    )
    title: str | None = Field(default=None, description="Title of the collection.")
    description: str | None = Field(default=None, description="Description of the collection.")
    parent_id: str | None = Field(
        default=None, alias="parentId", description="ID of the parent collection."
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the collection.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the collection.",
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the collection."
    )


class DeleteCollectionResult(APIModel):
    collections: list[Collection] | None = Field(default=None, description="Deleted collections.")


class DeleteCollectionArgs(RequestBody):
    collection_id: str = Field(
        ..., alias="collectionId", description="ID of the collection to delete."
    )


class DeleteCollectionsResult(APIModel):
    collections: list[Collection] | None = Field(default=None, description="Deleted collections.")


class DeleteCollectionsArgs(RequestBody):
    collection_ids: list[str] = Field(
        ..., alias="collectionIds", description="IDs of the collections to delete."
    )


class GetCollectionBreadcrumbsArgs(RequestBody):
    collection_id: str = Field(
        ...,
        alias="collectionId",
        description="ID of the collection whose breadcrumbs to retrieve.",
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in the response.",
    )


class GetCollectionArgs(RequestBody):
    collection_id: str = Field(
        ..., alias="collectionId", description="ID of the collection to retrieve."
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in the response.",
    )


class GetCollectionsByIdsArgs(RequestBody):
    collection_ids: list[str] = Field(
        ..., alias="collectionIds", description="IDs of the collections to retrieve."
    )


class GetStructureItemsArgs(RequestBody):
    collection_id: str | None = Field(
        ...,
        alias="collectionId",
        description="ID of the collection whose content to retrieve.",
    )
    page: str | None = Field(
        default=None,
        description="Token identifying the page of collection content to retrieve.",
    )
    filter_string: str | None = Field(
        default=None,
        alias="filterString",
        description="Filter collection content by title.",
    )
    order_field: Literal["title", "createdAt", "updatedAt"] | str | None = Field(
        default=None,
        alias="orderField",
        description="Field to order collection content by.",
    )
    order_direction: Literal["asc", "desc"] | str | None = Field(
        default=None,
        alias="orderDirection",
        description="Collection content sorting direction.",
    )
    only_my: bool | None = Field(
        default=None,
        alias="onlyMy",
        description="Return only items created by the current user.",
    )
    mode: Literal["all", "onlyCollections", "onlyWorkbooks", "onlyEntries"] | str | None = Field(
        default=None, description="Types of items to include in the response."
    )
    page_size: int | float | None = Field(
        default=None,
        alias="pageSize",
        description="Number of collection items per page.",
    )
    include_permissions_info: bool | None = Field(
        default=None,
        alias="includePermissionsInfo",
        description="Include permission information in the response.",
    )


class GetRootCollectionPermissionsResult(APIModel):
    create_collection_in_root: bool | None = Field(
        default=None,
        alias="createCollectionInRoot",
        description="Indicates if collections can be created in the root collection.",
    )
    create_workbook_in_root: bool | None = Field(
        default=None,
        alias="createWorkbookInRoot",
        description="Indicates if workbooks can be created in the root collection.",
    )


class MoveCollectionArgs(RequestBody):
    collection_id: str = Field(
        ..., alias="collectionId", description="ID of the collection to move."
    )
    parent_id: str | None = Field(
        ...,
        alias="parentId",
        description="ID of the parent collection to move the collection to.",
    )
    title: str | None = Field(default=None, description="New title of the collection.")


class MoveCollectionsArgs(RequestBody):
    collection_ids: list[str] = Field(
        ..., alias="collectionIds", description="IDs of the collections to move."
    )
    parent_id: str | None = Field(
        ...,
        alias="parentId",
        description="ID of the parent collection to move the collections to.",
    )


class UpdateCollectionArgs(RequestBody):
    collection_id: str = Field(
        ..., alias="collectionId", description="ID of the collection to update."
    )
    title: str | None = Field(default=None, description="New title of the collection.")
    description: str | None = Field(default=None, description="New description of the collection.")


class ListCollectionAccessBindingsArgs(RequestBody):
    collection_id: str = Field(
        ...,
        alias="collectionId",
        description="ID of the collection whose access bindings to retrieve.",
    )
    get_inherited_bindings: bool | None = Field(
        default=None,
        alias="getInheritedBindings",
        description="Include access bindings inherited from parent resources.",
    )
    page_size: int | float | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of subjects to return.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for retrieving the next page of results.",
    )


class OtherKindByEntity(APIModel):
    """A kind the specification does not describe: kept as it came."""

    entity: str | None = Field(default=None, description="The kind.")


class GetCollectionsByIdsResponse(RootModel[list[Collection]], hide_input_in_errors=True):
    root: list[Collection]


class MoveCollectionsResponse(APIModel):
    collections: list[Collection] | None = Field(default=None, description="Moved collections.")


class GetCollectionBreadcrumbsResultItemPermissions(APIModel):
    """Permissions for the collection."""

    list_access_bindings: bool | None = Field(
        default=None,
        alias="listAccessBindings",
        description="Indicates if access bindings for the collection can be listed.",
    )
    update_access_bindings: bool | None = Field(
        default=None,
        alias="updateAccessBindings",
        description="Indicates if access bindings for the collection can be updated.",
    )
    create_shared_entry: bool | None = Field(
        default=None,
        alias="createSharedEntry",
        description="Indicates if shared entries can be created in the collection.",
    )
    create_collection: bool | None = Field(
        default=None,
        alias="createCollection",
        description="Indicates if child collections can be created in the collection.",
    )
    create_workbook: bool | None = Field(
        default=None,
        alias="createWorkbook",
        description="Indicates if workbooks can be created in the collection.",
    )
    limited_view: bool | None = Field(
        default=None,
        alias="limitedView",
        description="Indicates if the collection can be viewed with limited access.",
    )
    view: bool | None = Field(
        default=None, description="Indicates if the collection can be viewed."
    )
    update: bool | None = Field(
        default=None, description="Indicates if the collection can be updated."
    )
    copy_: bool | None = Field(
        default=None,
        alias="copy",
        description="Indicates if the collection can be copied.",
    )
    move: bool | None = Field(default=None, description="Indicates if the collection can be moved.")
    delete: bool | None = Field(
        default=None, description="Indicates if the collection can be deleted."
    )
    browse: bool | None = Field(
        default=None,
        description="Indicates if the collection can be browsed as a transit node.",
    )


class GetCollectionResultPermissions(APIModel):
    """Permissions for the collection."""

    list_access_bindings: bool | None = Field(
        default=None,
        alias="listAccessBindings",
        description="Indicates if access bindings for the collection can be listed.",
    )
    update_access_bindings: bool | None = Field(
        default=None,
        alias="updateAccessBindings",
        description="Indicates if access bindings for the collection can be updated.",
    )
    create_shared_entry: bool | None = Field(
        default=None,
        alias="createSharedEntry",
        description="Indicates if shared entries can be created in the collection.",
    )
    create_collection: bool | None = Field(
        default=None,
        alias="createCollection",
        description="Indicates if child collections can be created in the collection.",
    )
    create_workbook: bool | None = Field(
        default=None,
        alias="createWorkbook",
        description="Indicates if workbooks can be created in the collection.",
    )
    limited_view: bool | None = Field(
        default=None,
        alias="limitedView",
        description="Indicates if the collection can be viewed with limited access.",
    )
    view: bool | None = Field(
        default=None, description="Indicates if the collection can be viewed."
    )
    update: bool | None = Field(
        default=None, description="Indicates if the collection can be updated."
    )
    copy_: bool | None = Field(
        default=None,
        alias="copy",
        description="Indicates if the collection can be copied.",
    )
    move: bool | None = Field(default=None, description="Indicates if the collection can be moved.")
    delete: bool | None = Field(
        default=None, description="Indicates if the collection can be deleted."
    )
    browse: bool | None = Field(
        default=None,
        description="Indicates if the collection can be browsed as a transit node.",
    )


class StructureItemEntryMeta(APIModel):
    """Entry metadata."""

    mode: str | None = None


class StructureItemEntryPermissions(APIModel):
    """Permissions for the entry."""

    list_access_bindings: bool | None = Field(
        default=None,
        alias="listAccessBindings",
        description="Permission to list access bindings.",
    )
    update_access_bindings: bool | None = Field(
        default=None,
        alias="updateAccessBindings",
        description="Permission to update access bindings.",
    )
    limited_view: bool | None = Field(
        default=None, alias="limitedView", description="Permission for limited viewing."
    )
    view: bool | None = Field(default=None, description="Permission to view.")
    update: bool | None = Field(default=None, description="Permission to update.")
    copy_: bool | None = Field(default=None, alias="copy", description="Permission to copy.")
    move: bool | None = Field(default=None, description="Permission to move.")
    delete: bool | None = Field(default=None, description="Permission to delete.")
    create_entry_binding: bool | None = Field(
        default=None,
        alias="createEntryBinding",
        description="Permission to create entry binding.",
    )
    create_limited_entry_binding: bool | None = Field(
        default=None,
        alias="createLimitedEntryBinding",
        description="Permission to create limited entry binding.",
    )


class GetStructureItemsResultItemsItemVariant1Permissions(APIModel):
    """Permissions for the collection."""

    list_access_bindings: bool | None = Field(
        default=None,
        alias="listAccessBindings",
        description="Indicates if access bindings for the collection can be listed.",
    )
    update_access_bindings: bool | None = Field(
        default=None,
        alias="updateAccessBindings",
        description="Indicates if access bindings for the collection can be updated.",
    )
    create_shared_entry: bool | None = Field(
        default=None,
        alias="createSharedEntry",
        description="Indicates if shared entries can be created in the collection.",
    )
    create_collection: bool | None = Field(
        default=None,
        alias="createCollection",
        description="Indicates if child collections can be created in the collection.",
    )
    create_workbook: bool | None = Field(
        default=None,
        alias="createWorkbook",
        description="Indicates if workbooks can be created in the collection.",
    )
    limited_view: bool | None = Field(
        default=None,
        alias="limitedView",
        description="Indicates if the collection can be viewed with limited access.",
    )
    view: bool | None = Field(
        default=None, description="Indicates if the collection can be viewed."
    )
    update: bool | None = Field(
        default=None, description="Indicates if the collection can be updated."
    )
    copy_: bool | None = Field(
        default=None,
        alias="copy",
        description="Indicates if the collection can be copied.",
    )
    move: bool | None = Field(default=None, description="Indicates if the collection can be moved.")
    delete: bool | None = Field(
        default=None, description="Indicates if the collection can be deleted."
    )
    browse: bool | None = Field(
        default=None,
        description="Indicates if the collection can be browsed as a transit node.",
    )


class Meta(APIModel):
    """Metadata associated with the workbook."""

    import_id: str | None = Field(
        default=None,
        alias="importId",
        description="ID of the workbook import operation.",
    )


class GetStructureItemsResultItemsItemVariant2Permissions(APIModel):
    """Permissions for the workbook."""

    list_access_bindings: bool | None = Field(
        default=None,
        alias="listAccessBindings",
        description="Indicates if access bindings for the workbook can be listed.",
    )
    update_access_bindings: bool | None = Field(
        default=None,
        alias="updateAccessBindings",
        description="Indicates if access bindings for the workbook can be updated.",
    )
    limited_view: bool | None = Field(
        default=None,
        alias="limitedView",
        description="Indicates if the workbook can be viewed with limited access.",
    )
    view: bool | None = Field(default=None, description="Indicates if the workbook can be viewed.")
    update: bool | None = Field(
        default=None, description="Indicates if the workbook can be updated."
    )
    copy_: bool | None = Field(
        default=None,
        alias="copy",
        description="Indicates if the workbook can be copied.",
    )
    move: bool | None = Field(default=None, description="Indicates if the workbook can be moved.")
    publish: bool | None = Field(
        default=None,
        description="Indicates if entries in the workbook can be published.",
    )
    embed: bool | None = Field(
        default=None,
        description="Indicates if entries in the workbook can be embedded.",
    )
    delete: bool | None = Field(
        default=None, description="Indicates if the workbook can be deleted."
    )


class CreateCollectionResult(APIModel):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="Unique identifier of the collection.",
    )
    title: str | None = Field(default=None, description="Title of the collection.")
    description: str | None = Field(default=None, description="Description of the collection.")
    parent_id: str | None = Field(
        default=None, alias="parentId", description="ID of the parent collection."
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the collection.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the collection.",
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the collection."
    )
    operation: shared.DatalensOperation | None = None


class GetCollectionResult(APIModel):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="Unique identifier of the collection.",
    )
    title: str | None = Field(default=None, description="Title of the collection.")
    description: str | None = Field(default=None, description="Description of the collection.")
    parent_id: str | None = Field(
        default=None, alias="parentId", description="ID of the parent collection."
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the collection.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the collection.",
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the collection."
    )
    permissions: GetCollectionResultPermissions | None = None


class StructureItemEntry(APIModel):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection the entry belongs to.",
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the entry.",
    )
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook the entry belongs to.",
    )
    scope: shared.EntryScope | None = None
    type: str | None = Field(default=None, description="Type of the entry.")
    key: str | None = Field(default=None, description="Key identifier of the entry.")
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the entry."
    )
    entity: Literal["entry"] = Field(..., description="Indicates that the item is an entry.")
    display_key: str | None = Field(
        default=None, alias="displayKey", description="Display key of the entry."
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the entry.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    title: str | None = Field(default=None, description="Title of the entry.")
    meta: StructureItemEntryMeta | None = None
    permissions: StructureItemEntryPermissions | None = None


class GetCollectionBreadcrumbsResultItem(APIModel):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="Unique identifier of the collection.",
    )
    title: str | None = Field(default=None, description="Title of the collection.")
    description: str | None = Field(default=None, description="Description of the collection.")
    parent_id: str | None = Field(
        default=None, alias="parentId", description="ID of the parent collection."
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the collection.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the collection.",
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the collection."
    )
    permissions: GetCollectionBreadcrumbsResultItemPermissions | None = None


class GetStructureItemsResultItemsItemVariant1(APIModel):
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="Unique identifier of the collection.",
    )
    title: str | None = Field(default=None, description="Title of the collection.")
    description: str | None = Field(default=None, description="Description of the collection.")
    parent_id: str | None = Field(
        default=None, alias="parentId", description="ID of the parent collection."
    )
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the collection.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the collection.",
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    meta: dict[str, Any] | None = Field(
        default=None, description="Metadata associated with the collection."
    )
    entity: Literal["collection"] = Field(
        ..., description="Indicates that the item is a collection."
    )
    permissions: GetStructureItemsResultItemsItemVariant1Permissions | None = None


class GetStructureItemsResultItemsItemVariant2(APIModel):
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="Unique identifier of the workbook.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection the workbook belongs to.",
    )
    title: str | None = Field(default=None, description="Title of the workbook.")
    description: str | None = Field(default=None, description="Description of the workbook.")
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the DataLens tenant."
    )
    meta: Meta | None = Field(default=None, description="Metadata associated with the workbook.")
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the workbook.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the workbook.",
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last update timestamp."
    )
    status: Literal["creating", "deleting", "active", "deleted"] | str | None = Field(
        default=None, description="Status of the workbook."
    )
    entity: Literal["workbook"] = Field(..., description="Indicates that the item is a workbook.")
    permissions: GetStructureItemsResultItemsItemVariant2Permissions | None = None


class GetCollectionBreadcrumbsResult(
    RootModel[list[GetCollectionBreadcrumbsResultItem]], hide_input_in_errors=True
):
    root: list[GetCollectionBreadcrumbsResultItem]


class GetStructureItemsResult(APIModel):
    items: (
        list[
            GetStructureItemsResultItemsItemVariant1
            | GetStructureItemsResultItemsItemVariant2
            | StructureItemEntry
            | OtherKindByEntity
        ]
        | None
    ) = Field(default=None, description="List of collection content items.")
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for retrieving the next page of results.",
    )


class UpdateCollectionAccessBindingsArgs(RequestBody):
    collection_id: str = Field(
        ...,
        alias="collectionId",
        description="ID of the collection whose access bindings to update.",
    )
    deltas: list[shared.USAccessBindingDelta] = Field(
        ..., description="Access binding changes to apply."
    )
