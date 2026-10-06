"""DataLens audit operations, declared once (sans-IO).

Examples:
    >>> entry_permissions_get(["ent1"], user_id="user-1").body
    {'entryIds': ['ent1'], 'userId': 'user-1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.core.pagination import BodyCursorPagination
from ycli.yandex.datalens.audit.models import AuditEntriesPage, AuditEntry, UserEntryPermissions
from ycli.yandex.datalens.cursor import next_page_token
from ycli.yandex.datalens.schemas.audit import (
    GetAuditEntriesUpdatesArgs,
    GetAuditEntryPermissionsForUserArgs,
)

# The size of a page is called ``limit`` here, where the other listings call it ``pageSize``:
# it is the pager's field, and the method's ``limit`` stays ycli's cap on the whole listing.
AUDIT_CURSOR = BodyCursorPagination(cursor_of=next_page_token, size_param="limit")


def entries_updates_list(from_: str, *, to: str | None) -> Paged[AuditEntriesPage, AuditEntry]:
    body = GetAuditEntriesUpdatesArgs.model_validate({"from": from_, "to": to})
    return Paged(
        RPC("getAuditEntriesUpdates", AuditEntriesPage, json=body, effect=Effect.READ),
        AUDIT_CURSOR,
        lambda page: page.entries or [],
    )


def entry_permissions_get(
    entry_ids: Sequence[str], *, user_id: str
) -> Endpoint[UserEntryPermissions]:
    body = GetAuditEntryPermissionsForUserArgs(entryIds=list(entry_ids), userId=user_id)
    return RPC(
        "getAuditEntryPermissionsForUser", UserEntryPermissions, json=body, effect=Effect.READ
    )
