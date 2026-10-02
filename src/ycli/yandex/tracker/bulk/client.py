"""Tracker bulk-change client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.bulk.endpoints`. The three
trigger calls (update/move/transition) each start an *async* operation and return a
:class:`~ycli.yandex.tracker.bulk.models.BulkChange`; the reads (:meth:`get`, :meth:`issues`)
let a caller poll it to a terminal state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.bulk import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.bulk.models import BulkChange, BulkIssueResultList


class BulkClient(Resource):
    """``/bulkchange`` (mass update/move/transition + status reads)."""

    def update(self, body: dict[str, Any]) -> BulkChange:
        """``POST /bulkchange/_update`` — mass-edit issues. Returns the started ``BulkChange``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.update(
            ...     {"issues": ["TEST-1"], "values": {"priority": {"key": "blocker"}}}
            ... ).status  # doctest: +SKIP
            'CREATED'
        """
        return self._session.send(endpoints.update_bulk(body))

    def move(self, body: dict[str, Any]) -> BulkChange:
        """``POST /bulkchange/_move`` — mass-move issues to another queue. Returns a ``BulkChange``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.move({"queue": "CHECK", "issues": ["TEST-1"]}).id  # doctest: +SKIP
            '1ab23cd4…'
        """
        return self._session.send(endpoints.move_bulk(body))

    def transition(self, body: dict[str, Any]) -> BulkChange:
        """``POST /bulkchange/_transition`` — mass status transition. Returns a ``BulkChange``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.transition(
            ...     {"transition": "close", "issues": ["TEST-1"]}
            ... ).status  # doctest: +SKIP
            'CREATED'
        """
        return self._session.send(endpoints.transition_bulk(body))

    def get(self, bulk_id: str) -> BulkChange:
        """``GET /bulkchange/{bulk_id}`` → the operation's current status (poll this to wait).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.get("1ab23cd4…").is_terminal  # doctest: +SKIP
            True
        """
        return self._session.send(endpoints.get_bulk(bulk_id))

    def issues(self, bulk_id: str) -> BulkIssueResultList:
        """``GET /bulkchange/{bulk_id}/issues`` → issues for which the operation failed.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.issues("1ab23cd4…").root[0].issue  # doctest: +SKIP
            'TEST-1'
        """
        return self._session.send(endpoints.list_bulk_issues(bulk_id))
