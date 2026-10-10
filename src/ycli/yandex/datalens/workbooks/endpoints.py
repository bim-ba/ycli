"""DataLens workbook operations, declared once (sans-IO).

Examples:
    >>> get("w1", include_permissions_info=None).body
    {'workbookId': 'w1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR, DATALENS_PAGE_NUMBER
from ycli.yandex.datalens.models import (
    AccessBindingDelta,
    AccessBindingsPage,
    Operation,
    OrderField,
    SubjectWithBindings,
)
from ycli.yandex.datalens.schemas.workbook import (
    CreateWorkbookArgs,
    DeleteWorkbookArgs,
    DeleteWorkbooksArgs,
    GetWorkbookArgs,
    GetWorkbookEntriesArgs,
    GetWorkbooksByIdsArgs,
    GetWorkbooksListArgs,
    ListWorkbookAccessBindingsArgs,
    MoveWorkbookArgs,
    MoveWorkbooksArgs,
    UpdateWorkbookAccessBindingsArgs,
    UpdateWorkbookArgs,
)
from ycli.yandex.datalens.workbooks.models import (
    EntriesFilters,
    EntriesOrder,
    EntriesPage,
    EntryScope,
    Workbook,
    WorkbookCreated,
    WorkbookDetails,
    WorkbookEntry,
    WorkbookListed,
    WorkbooksDeleted,
    WorkbooksMoved,
    WorkbooksPage,
)
from ycli.yandex.models import ItemList, SortDirection


def get(workbook_id: str, *, include_permissions_info: bool | None) -> Endpoint[WorkbookDetails]:
    body = GetWorkbookArgs(workbookId=workbook_id, includePermissionsInfo=include_permissions_info)
    return RPC("getWorkbook", WorkbookDetails, json=body, effect=Effect.READ)


def list_(
    *,
    collection_id: str | None,
    filter_string: str | None,
    order_field: OrderField | None,
    order_direction: SortDirection | None,
    only_my: bool | None,
    include_permissions_info: bool | None,
) -> Paged[WorkbooksPage, WorkbookListed]:
    body = GetWorkbooksListArgs(
        collectionId=collection_id,
        filterString=filter_string,
        orderField=order_field,
        orderDirection=order_direction,
        onlyMy=only_my,
        includePermissionsInfo=include_permissions_info,
    )
    return Paged(
        RPC("getWorkbooksList", WorkbooksPage, json=body, effect=Effect.READ),
        DATALENS_PAGE_NUMBER,
        lambda page: page.workbooks or [],
    )


def list_by_ids(workbook_ids: Sequence[str]) -> Endpoint[ItemList[Workbook]]:
    body = GetWorkbooksByIdsArgs(workbookIds=list(workbook_ids))
    return RPC("getWorkbooksByIds", ItemList[Workbook], json=body, effect=Effect.READ)


def entries_list(
    workbook_id: str,
    *,
    include_permissions_info: bool | None,
    only_my: bool | None,
    created_by: str | None,
    scope: EntryScope | Sequence[EntryScope] | None,
    order_by: EntriesOrder | None,
    filters: EntriesFilters | None,
) -> Paged[EntriesPage, WorkbookEntry]:
    body = GetWorkbookEntriesArgs.model_validate(
        {
            "workbookId": workbook_id,
            "includePermissionsInfo": include_permissions_info,
            "onlyMy": only_my,
            "createdBy": created_by,
            # One scope goes as it is, several as a list: the API takes either.
            "scope": scope if scope is None or isinstance(scope, str) else list(scope),
            "orderBy": order_by,
            "filters": filters,
        }
    )
    return Paged(
        RPC("getWorkbookEntries", EntriesPage, json=body, effect=Effect.READ),
        DATALENS_PAGE_NUMBER,
        lambda page: page.entries or [],
    )


def access_bindings_list(
    workbook_id: str, *, get_inherited_bindings: bool | None
) -> Paged[AccessBindingsPage, SubjectWithBindings]:
    body = ListWorkbookAccessBindingsArgs(
        workbookId=workbook_id, getInheritedBindings=get_inherited_bindings
    )
    return Paged(
        RPC("listWorkbookAccessBindings", AccessBindingsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.subjects_with_bindings or [],
    )


def create(
    *, title: str, collection_id: str | None, description: str | None
) -> Endpoint[WorkbookCreated]:
    body = CreateWorkbookArgs(title=title, collectionId=collection_id, description=description)
    return RPC("createWorkbook", WorkbookCreated, json=body, effect=Effect.WRITE)


def update(workbook_id: str, *, title: str | None, description: str | None) -> Endpoint[Workbook]:
    body = UpdateWorkbookArgs(workbookId=workbook_id, title=title, description=description)
    return RPC("updateWorkbook", Workbook, json=body, effect=Effect.IDEMPOTENT_WRITE)


def move(workbook_id: str, *, collection_id: str | None, title: str | None) -> Endpoint[Workbook]:
    body = MoveWorkbookArgs(workbookId=workbook_id, collectionId=collection_id, title=title)
    return RPC("moveWorkbook", Workbook, json=body, effect=Effect.WRITE)


def move_bulk(
    workbook_ids: Sequence[str], *, collection_id: str | None
) -> Endpoint[WorkbooksMoved]:
    body = MoveWorkbooksArgs(workbookIds=list(workbook_ids), collectionId=collection_id)
    return RPC("moveWorkbooks", WorkbooksMoved, json=body, effect=Effect.WRITE)


def delete(workbook_id: str) -> Endpoint[Workbook]:
    body = DeleteWorkbookArgs(workbookId=workbook_id)
    return RPC("deleteWorkbook", Workbook, json=body, effect=Effect.DESTRUCTIVE)


def delete_bulk(workbook_ids: Sequence[str]) -> Endpoint[WorkbooksDeleted]:
    body = DeleteWorkbooksArgs(workbookIds=list(workbook_ids))
    return RPC("deleteWorkbooks", WorkbooksDeleted, json=body, effect=Effect.DESTRUCTIVE)


def access_bindings_update(
    workbook_id: str, *, deltas: Sequence[AccessBindingDelta]
) -> Endpoint[Operation]:
    body = UpdateWorkbookAccessBindingsArgs(workbookId=workbook_id, deltas=list(deltas))
    return RPC(
        "updateWorkbookAccessBindings",
        Operation,
        json=body,
        effect=Effect.WRITE,
        grants_access=True,
    )
