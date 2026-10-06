"""DataLens permissions client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.permissions import endpoints

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.datalens.permissions.models import PermissionsBulk


class PermissionsClient(Resource):
    """Permissions: what the caller may do with entries, workbooks and collections."""

    def get_bulk(
        self,
        *,
        entry_ids: Sequence[str] | None = None,
        workbook_ids: Sequence[str] | None = None,
        collection_ids: Sequence[str] | None = None,
    ) -> PermissionsBulk:
        """``getPermissionsBulk`` → the caller's permissions on many objects at once.

        Each of the three maps is keyed by id: an object the caller can see gives its
        ``permissions``, one that does not exist gives ``error: "NOT_FOUND"``. An id of a wrong
        form refuses the whole request (400).

        Args:
            entry_ids: The ids of entries.
            workbook_ids: The ids of workbooks.
            collection_ids: The ids of collections.

        Returns:
            Three maps, ``entries``, ``workbooks`` and ``collections``, id → what was found.

        Examples:
            >>> found = datalens.permissions.get_bulk(
            ...     workbook_ids=["wb000000000001", "wb000000000009"]
            ... )
            >>> found.workbooks["wb000000000001"].permissions.update
            True
            >>> found.workbooks["wb000000000009"].error
            'NOT_FOUND'
        """
        return self._session.send(
            endpoints.get_bulk(
                entry_ids=entry_ids, workbook_ids=workbook_ids, collection_ids=collection_ids
            )
        )
