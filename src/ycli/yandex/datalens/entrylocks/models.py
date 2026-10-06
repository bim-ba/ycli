"""DataLens entry lock models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.entry_lock import CreateEntryLockArgsData as LockTerms
from ycli.yandex.datalens.schemas.entry_lock import CreateEntryLockResult as LockCreated
from ycli.yandex.datalens.schemas.entry_lock import DeleteEntryLockArgsParams as LockRelease
from ycli.yandex.datalens.schemas.entry_lock import EntryLock as Lock
from ycli.yandex.datalens.schemas.entry_lock import ExtendEntryLockArgsData as LockExtension

__all__ = ["Lock", "LockCreated", "LockExtension", "LockRelease", "LockTerms"]
