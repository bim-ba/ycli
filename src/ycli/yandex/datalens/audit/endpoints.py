"""DataLens audit operations, declared once (sans-IO).

Examples:
    >>> entry_permissions_get(["ent1"], user_id="user-1").body
    {'entryIds': ['ent1'], 'userId': 'user-1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.audit.models import AuditEntriesPage, AuditEntry, UserEntryPermissions
from ycli.yandex.datalens.cursor import DATALENS_CURSOR_SIZED_BY_LIMIT
from ycli.yandex.datalens.schemas.audit import (
    GetAuditEntriesUpdatesArgs,
    GetAuditEntryPermissionsForUserArgs,
)


def entries_updates_list(from_: str, *, to: str | None) -> Paged[AuditEntriesPage, AuditEntry]:
    body = GetAuditEntriesUpdatesArgs.model_validate({"from": from_, "to": to})
    return Paged(
        RPC("getAuditEntriesUpdates", AuditEntriesPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR_SIZED_BY_LIMIT,
        lambda page: page.entries or [],
    )


def entry_permissions_get(
    entry_ids: Sequence[str], *, user_id: str
) -> Endpoint[UserEntryPermissions]:
    body = GetAuditEntryPermissionsForUserArgs(entryIds=list(entry_ids), userId=user_id)
    return RPC(
        "getAuditEntryPermissionsForUser", UserEntryPermissions, json=body, effect=Effect.READ
    )
