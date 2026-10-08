"""Tracker bulk-change client on the httpx2 core.

``issues.update_bulk``, ``move_bulk`` and ``transition_bulk`` each start an *async* operation
and return a :class:`~ycli.yandex.tracker.bulk.models.BulkChange`; the reads here
(:meth:`get`, :meth:`issues_list`) let a caller poll it to a terminal state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.bulk import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.bulk.models import (
        BulkChange,
        BulkIssueResult,
    )


class BulkClient(Resource):
    """``/bulkchange``: the status of a bulk change and the issues it failed on."""

    def get(self, bulk_id: str) -> BulkChange:
        """``GET /bulkchange/{bulk_id}`` → the operation's current status (poll this to wait).

        Args:
            bulk_id: The bulk change's id.

        Returns:
            The bulk change with its current status.

        Examples:
            >>> tracker.bulk.get("4gh").is_terminal
            True
        """
        return self._session.send(endpoints.get(bulk_id))

    def issues_list(self, bulk_id: str) -> ItemList[BulkIssueResult]:
        """``GET /bulkchange/{bulk_id}/issues`` → every issue of the change, with how it went.

        One record per issue, the ones that went well too: after a change that passed, each
        reads ``COMPLETED`` (measured); a failed one carries its ``error``.

        Args:
            bulk_id: The bulk change's id.

        Returns:
            The per-issue results.

        Examples:
            >>> tracker.bulk.issues_list("5ij").root[0].issue
            'DE-9'
        """
        return self._session.send(endpoints.issues_list(bulk_id))
