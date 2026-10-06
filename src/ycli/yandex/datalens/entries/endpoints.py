"""DataLens entry operations, declared once (sans-IO).

Examples:
    >>> rename("e1", name="Sales").body
    {'entryId': 'e1', 'name': 'Sales'}
"""

from collections.abc import Sequence
from dataclasses import replace

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.entries.models import (
    EntriesPage,
    EntriesPermissions,
    Entry,
    ListFilters,
    ListOrder,
    Relation,
    RelationsPage,
    Renamed,
    Revision,
    RevisionsPage,
)
from ycli.yandex.datalens.models import EntryScope
from ycli.yandex.datalens.schemas.entries import (
    GetEntriesPermissionsArgs,
    GetEntriesRelationsArgs,
    GetRevisionsArgs,
    RenameEntryArgs,
)
from ycli.yandex.datalens.schemas.navigation import GetEntriesV2Args
from ycli.yandex.models import ItemList


def _listed(values: Sequence[str] | None) -> list[str] | None:
    return None if values is None else list(values)


def list_(
    *,
    ids: Sequence[str] | None,
    scope: EntryScope | None,
    scopes: Sequence[EntryScope] | None,
    type: str | Sequence[str] | None,  # noqa: A002  # the API's own name for it
    created_by: Sequence[str] | None,
    order_by: ListOrder | None,
    exclude_locked: bool | None,
    include_links: bool | None,
    filters: ListFilters | None,
    include_permissions_info: bool | None,
    ignore_workbook_entries: bool | None,
    ignore_shared_entries: bool | None,
    include_data: bool | None,
) -> Paged[EntriesPage, Entry]:
    body = GetEntriesV2Args.model_validate(
        {
            "ids": _listed(ids),
            "scope": scope,
            "scopes": _listed(scopes),
            # One type goes as it is, several as a list: the API takes either.
            "type": type if type is None or isinstance(type, str) else list(type),
            "createdBy": _listed(created_by),
            "orderBy": order_by,
            "excludeLocked": exclude_locked,
            "includeLinks": include_links,
            "filters": filters,
            "includePermissionsInfo": include_permissions_info,
            "ignoreWorkbookEntries": ignore_workbook_entries,
            "ignoreSharedEntries": ignore_shared_entries,
            "includeData": include_data,
        }
    )
    return Paged(
        RPC("getEntries", EntriesPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.entries or [],
    )


def relations_list(
    entry_ids: Sequence[str],
    *,
    link_direction: str | None,
    include_permissions_info: bool | None,
    scope: EntryScope | None,
) -> Paged[RelationsPage, Relation]:
    body = GetEntriesRelationsArgs.model_validate(
        {
            "entryIds": list(entry_ids),
            "linkDirection": link_direction,
            "includePermissionsInfo": include_permissions_info,
            "scope": scope,
        }
    )
    return Paged(
        RPC("getEntriesRelations", RelationsPage, json=body, effect=Effect.READ),
        # This listing names its page size ``limit``.
        replace(DATALENS_CURSOR, size_param="limit"),
        lambda page: page.relations or [],
    )


def permissions_get(entry_ids: Sequence[str]) -> Endpoint[EntriesPermissions]:
    body = GetEntriesPermissionsArgs(entryIds=list(entry_ids))
    return RPC("getEntriesPermissions", EntriesPermissions, json=body, effect=Effect.READ)


def revisions_list(
    entry_id: str, *, rev_ids: Sequence[str] | None
) -> Paged[RevisionsPage, Revision]:
    body = GetRevisionsArgs(entryId=entry_id, revIds=_listed(rev_ids))
    return Paged(
        RPC("getRevisions", RevisionsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.entries or [],
    )


def rename(entry_id: str, *, name: str) -> Endpoint[ItemList[Renamed]]:
    body = RenameEntryArgs(entryId=entry_id, name=name)
    return RPC("renameEntry", ItemList[Renamed], json=body, effect=Effect.IDEMPOTENT_WRITE)
