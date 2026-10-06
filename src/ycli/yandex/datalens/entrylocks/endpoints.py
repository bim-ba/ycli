"""DataLens entry lock operations, declared once (sans-IO).

Examples:
    >>> from ycli.yandex.datalens.entrylocks.models import LockTerms
    >>> create("e1", data=LockTerms(duration=300000)).body
    {'entryId': 'e1', 'data': {'duration': 300000}}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.entrylocks.models import (
    Lock,
    LockCreated,
    LockExtension,
    LockRelease,
    LockTerms,
)
from ycli.yandex.datalens.schemas.entry_lock import (
    CreateEntryLockArgs,
    DeleteEntryLockArgs,
    ExtendEntryLockArgs,
)


def create(entry_id: str, *, data: LockTerms) -> Endpoint[LockCreated]:
    body = CreateEntryLockArgs(entryId=entry_id, data=data)
    return RPC("createEntryLock", LockCreated, json=body, effect=Effect.WRITE)


def extend(entry_id: str, *, data: LockExtension) -> Endpoint[Lock]:
    body = ExtendEntryLockArgs(entryId=entry_id, data=data)
    return RPC("extendEntryLock", Lock, json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(entry_id: str, *, params: LockRelease) -> Endpoint[Lock]:
    body = DeleteEntryLockArgs(entryId=entry_id, params=params)
    return RPC("deleteEntryLock", Lock, json=body, effect=Effect.DESTRUCTIVE)
