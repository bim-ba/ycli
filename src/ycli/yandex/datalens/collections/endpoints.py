"""DataLens collection operations, declared once (sans-IO).

Examples:
    >>> get("c1", include_permissions_info=None).body
    {'collectionId': 'c1'}
"""

from collections.abc import Sequence
from dataclasses import replace

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.collections.models import (
    Collection,
    CollectionBreadcrumb,
    CollectionCreated,
    CollectionDetails,
    CollectionsDeleted,
    CollectionsMoved,
    ContentItem,
    ContentMode,
    ContentPage,
    RootPermissions,
)
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.models import (
    AccessBindingDelta,
    AccessBindingsPage,
    Operation,
    OrderField,
    SubjectWithBindings,
)
from ycli.yandex.datalens.schemas.collection import (
    CreateCollectionArgs,
    DeleteCollectionArgs,
    DeleteCollectionsArgs,
    GetCollectionArgs,
    GetCollectionBreadcrumbsArgs,
    GetCollectionsByIdsArgs,
    GetStructureItemsArgs,
    ListCollectionAccessBindingsArgs,
    MoveCollectionArgs,
    MoveCollectionsArgs,
    UpdateCollectionAccessBindingsArgs,
    UpdateCollectionArgs,
)
from ycli.yandex.models import ItemList, SortDirection


def get(
    collection_id: str, *, include_permissions_info: bool | None
) -> Endpoint[CollectionDetails]:
    body = GetCollectionArgs(
        collectionId=collection_id, includePermissionsInfo=include_permissions_info
    )
    return RPC("getCollection", CollectionDetails, json=body, effect=Effect.READ)


def list_by_ids(collection_ids: Sequence[str]) -> Endpoint[ItemList[Collection]]:
    body = GetCollectionsByIdsArgs(collectionIds=list(collection_ids))
    return RPC("getCollectionsByIds", ItemList[Collection], json=body, effect=Effect.READ)


def content_list(
    collection_id: str | None,
    *,
    filter_string: str | None,
    order_field: OrderField | None,
    order_direction: SortDirection | None,
    only_my: bool | None,
    mode: ContentMode | None,
    include_permissions_info: bool | None,
) -> Paged[ContentPage, ContentItem]:
    body = GetStructureItemsArgs(
        collectionId=collection_id,
        filterString=filter_string,
        orderField=order_field,
        orderDirection=order_direction,
        onlyMy=only_my,
        mode=mode,
        includePermissionsInfo=include_permissions_info,
    )
    return Paged(
        RPC("getCollectionContent", ContentPage, json=body, effect=Effect.READ),
        # This one listing takes the token back as ``page``.
        replace(DATALENS_CURSOR, cursor_param="page"),
        lambda page: page.items or [],
    )


def breadcrumbs_list(
    collection_id: str, *, include_permissions_info: bool | None
) -> Endpoint[ItemList[CollectionBreadcrumb]]:
    body = GetCollectionBreadcrumbsArgs(
        collectionId=collection_id, includePermissionsInfo=include_permissions_info
    )
    return RPC(
        "getCollectionBreadcrumbs", ItemList[CollectionBreadcrumb], json=body, effect=Effect.READ
    )


def permissions_get_root() -> Endpoint[RootPermissions]:
    return RPC("getRootCollectionPermissions", RootPermissions, effect=Effect.READ)


def access_bindings_list(
    collection_id: str, *, get_inherited_bindings: bool | None
) -> Paged[AccessBindingsPage, SubjectWithBindings]:
    body = ListCollectionAccessBindingsArgs(
        collectionId=collection_id, getInheritedBindings=get_inherited_bindings
    )
    return Paged(
        RPC("listCollectionAccessBindings", AccessBindingsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.subjects_with_bindings or [],
    )


def create(
    *, title: str, parent_id: str | None, description: str | None
) -> Endpoint[CollectionCreated]:
    body = CreateCollectionArgs(title=title, parentId=parent_id, description=description)
    return RPC("createCollection", CollectionCreated, json=body, effect=Effect.WRITE)


def update(
    collection_id: str, *, title: str | None, description: str | None
) -> Endpoint[Collection]:
    body = UpdateCollectionArgs(collectionId=collection_id, title=title, description=description)
    return RPC("updateCollection", Collection, json=body, effect=Effect.IDEMPOTENT_WRITE)


def move(collection_id: str, *, parent_id: str | None, title: str | None) -> Endpoint[Collection]:
    body = MoveCollectionArgs(collectionId=collection_id, parentId=parent_id, title=title)
    return RPC("moveCollection", Collection, json=body, effect=Effect.WRITE)


def move_bulk(
    collection_ids: Sequence[str], *, parent_id: str | None
) -> Endpoint[CollectionsMoved]:
    body = MoveCollectionsArgs(collectionIds=list(collection_ids), parentId=parent_id)
    return RPC("moveCollections", CollectionsMoved, json=body, effect=Effect.WRITE)


def delete(collection_id: str) -> Endpoint[CollectionsDeleted]:
    body = DeleteCollectionArgs(collectionId=collection_id)
    return RPC("deleteCollection", CollectionsDeleted, json=body, effect=Effect.DESTRUCTIVE)


def delete_bulk(collection_ids: Sequence[str]) -> Endpoint[CollectionsDeleted]:
    body = DeleteCollectionsArgs(collectionIds=list(collection_ids))
    return RPC("deleteCollections", CollectionsDeleted, json=body, effect=Effect.DESTRUCTIVE)


def access_bindings_update(
    collection_id: str, *, deltas: Sequence[AccessBindingDelta]
) -> Endpoint[Operation]:
    body = UpdateCollectionAccessBindingsArgs(collectionId=collection_id, deltas=list(deltas))
    return RPC("updateCollectionAccessBindings", Operation, json=body, effect=Effect.WRITE)
