# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class GetPermissionsBulkArgs(RequestBody):
    entry_ids: list[str] | None = Field(
        default=None,
        alias="entryIds",
        description="Identifiers of the entries to check permissions for.",
    )
    workbook_ids: list[str] | None = Field(
        default=None,
        alias="workbookIds",
        description="Identifiers of the workbooks to check permissions for.",
    )
    collection_ids: list[str] | None = Field(
        default=None,
        alias="collectionIds",
        description="Identifiers of the collections to check permissions for.",
    )


class GetPermissionsBulkResultEntriesValuePermissions(APIModel):
    """Basic permissions for the entry."""

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


class GetPermissionsBulkResultEntriesValueFullPermissions(APIModel):
    """Full permissions for the entry."""

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
    get: bool | None = Field(default=None, description="Permission to read compute entry metadata.")
    use: bool | None = Field(default=None, description="Permission to use the compute resource.")


class GetPermissionsBulkResultWorkbooksValuePermissions(APIModel):
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


class GetPermissionsBulkResultCollectionsValuePermissions(APIModel):
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


class GetPermissionsBulkResultEntriesValue(APIModel):
    permissions: GetPermissionsBulkResultEntriesValuePermissions | None = None
    full_permissions: GetPermissionsBulkResultEntriesValueFullPermissions | None = Field(
        default=None, alias="fullPermissions"
    )
    error: Literal["NOT_FOUND"] | str | None = Field(
        default=None, description="Error code indicating a missing resource."
    )


class GetPermissionsBulkResultWorkbooksValue(APIModel):
    permissions: GetPermissionsBulkResultWorkbooksValuePermissions | None = None
    error: Literal["NOT_FOUND"] | str | None = Field(
        default=None, description="Error code indicating a missing resource."
    )


class GetPermissionsBulkResultCollectionsValue(APIModel):
    permissions: GetPermissionsBulkResultCollectionsValuePermissions | None = None
    error: Literal["NOT_FOUND"] | str | None = Field(
        default=None, description="Error code indicating a missing resource."
    )


class GetPermissionsBulkResult(APIModel):
    entries: dict[str, GetPermissionsBulkResultEntriesValue] | None = Field(
        default=None, description="Entry permissions or errors indexed by entry ID."
    )
    workbooks: dict[str, GetPermissionsBulkResultWorkbooksValue] | None = Field(
        default=None,
        description="Workbook permissions or errors indexed by workbook ID.",
    )
    collections: dict[str, GetPermissionsBulkResultCollectionsValue] | None = Field(
        default=None,
        description="Collection permissions or errors indexed by collection ID.",
    )
