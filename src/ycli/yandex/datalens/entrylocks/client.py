"""DataLens entry locks client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.entrylocks import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.entrylocks.models import (
        Lock,
        LockCreated,
        LockExtension,
        LockRelease,
        LockTerms,
    )


class EntryLocksClient(Resource):
    """Locks on entries: the hold an editor takes on a dataset, a chart or a dashboard."""

    def create(self, entry_id: str, *, data: LockTerms) -> LockCreated:
        """``createEntryLock`` — lock an entry for editing.

        The reply is the token alone: keep it, releasing and extending the lock take it.
        An entry that is already locked answers 423 ``ERR.US.ENTRY_IS_LOCKED`` with who holds
        the lock and until when, unless ``force`` is given.

        Args:
            entry_id: The entry's id.
            data: How long to hold the lock, in milliseconds, and whether to replace a lock
                that is already there.

        Returns:
            The token of the lock: extending and releasing it take the token.

        Examples:
            >>> from ycli.yandex.datalens.entrylocks.models import LockTerms
            >>> created = datalens.entrylocks.create(
            ...     "ent00000000001", data=LockTerms(duration=300000)
            ... )
            >>> created.lock_token
            'lock-token-1'
        """
        return self._session.send(endpoints.create(entry_id, data=data))

    def extend(self, entry_id: str, *, data: LockExtension) -> Lock:
        """``extendEntryLock`` — hold a lock longer.

        Args:
            entry_id: The entry's id.
            data: The token of the lock and the new duration, in milliseconds.

        Returns:
            The lock as it is now, with when it expires.

        Examples:
            >>> from ycli.yandex.datalens.entrylocks.models import LockExtension
            >>> terms = LockExtension(lock_token="lock-token-1", duration=600000)
            >>> datalens.entrylocks.extend("ent00000000001", data=terms).expiry_date
            '2026-10-06T12:10:00.000Z'
        """
        return self._session.send(endpoints.extend(entry_id, data=data))

    def delete(self, entry_id: str, *, params: LockRelease) -> Lock:
        """``deleteEntryLock`` — release a lock.

        An entry that is not locked answers 404 ``NOT_EXIST_LOCKED_ENTRY``.

        Args:
            entry_id: The entry's id.
            params: The token of the lock, or ``force`` to release a lock held by another.

        Returns:
            The lock that was released.

        Examples:
            >>> from ycli.yandex.datalens.entrylocks.models import LockRelease
            >>> released = datalens.entrylocks.delete(
            ...     "ent00000000001", params=LockRelease(lock_token="lock-token-1")
            ... )
            >>> released.entry_id
            'ent00000000001'
        """
        return self._session.send(endpoints.delete(entry_id, params=params))
