"""DataLens audit client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.audit import endpoints
from ycli.yandex.datalens.audit.models import AuditEntry
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.datalens.audit.models import UserEntryPermissions


class AuditClient(Resource):
    """Audit: which entries changed and when, and what one user may do with an entry."""

    def entries_updates_list(
        self, from_: str, *, to: str | None = None, limit: int | None = None
    ) -> ItemList[AuditEntry]:
        """``getAuditEntriesUpdates`` → the entries changed in a period, draining the pages.

        Capped at ``limit`` (``None`` = every entry). A deleted entry is listed too, with
        ``is_deleted``.

        Args:
            from_: The start of the period, an ISO-8601 time with its zone.
            to: The end of the period.
            limit: The most entries to return; ``None`` returns every entry.

        Returns:
            The entries changed in the period: what each is, when it changed and who did it.

        Examples:
            >>> changed = datalens.audit.entries_updates_list("2026-10-01T00:00:00Z").root
            >>> [(entry.entry_id, entry.is_deleted) for entry in changed]
            [('ent0000000001', False), ('ent0000000002', True)]
        """
        paged = endpoints.entries_updates_list(from_, to=to)
        return ItemList[AuditEntry](list(self._session.iterate(paged, limit=limit)))

    def entry_permissions_get(
        self, entry_ids: Sequence[str], *, user_id: str
    ) -> UserEntryPermissions:
        """``getAuditEntryPermissionsForUser`` → what one user may do with each entry.

        Args:
            entry_ids: The ids of the entries to ask about.
            user_id: The user's id, as ``createdBy`` of an entry gives it.

        Returns:
            By entry id: ``permissions`` (execute, read, edit, admin), or ``error`` for an entry
            that does not exist.

        Examples:
            >>> answer = datalens.audit.entry_permissions_get(
            ...     ["ent0000000001"], user_id="user-1"
            ... ).root
            >>> answer["ent0000000001"].permissions.edit
            True
        """
        return self._session.send(endpoints.entry_permissions_get(entry_ids, user_id=user_id))
