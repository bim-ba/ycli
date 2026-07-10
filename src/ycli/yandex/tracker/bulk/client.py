"""Declarative Tracker bulk-change client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

The three trigger calls (update/move/transition) each start an *async* operation and return a
:class:`~ycli.yandex.tracker.bulk.models.BulkChange`; the reads (:meth:`get`, :meth:`issues`)
let a caller poll it to a terminal state.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.bulk.models import BulkChange, BulkIssueResultList


class BulkClient(TrackerResource):
    """Declarative HTTP for ``/bulkchange`` (mass update/move/transition + status reads)."""

    @uplink.returns.json()
    @uplink.json
    @uplink.post("bulkchange/_update")
    def update(self, body: uplink.Body) -> BulkChange:  # ty: ignore[empty-body]
        """``POST /bulkchange/_update`` — mass-edit issues. Returns the started ``BulkChange``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.update(
            ...     {"issues": ["TEST-1"], "values": {"priority": {"key": "blocker"}}}
            ... ).status  # doctest: +SKIP
            'CREATED'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("bulkchange/_move")
    def move(self, body: uplink.Body) -> BulkChange:  # ty: ignore[empty-body]
        """``POST /bulkchange/_move`` — mass-move issues to another queue. Returns a ``BulkChange``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.move({"queue": "CHECK", "issues": ["TEST-1"]}).id  # doctest: +SKIP
            '1ab23cd4…'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("bulkchange/_transition")
    def transition(self, body: uplink.Body) -> BulkChange:  # ty: ignore[empty-body]
        """``POST /bulkchange/_transition`` — mass status transition. Returns a ``BulkChange``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.transition(
            ...     {"transition": "close", "issues": ["TEST-1"]}
            ... ).status  # doctest: +SKIP
            'CREATED'
        """

    @uplink.returns.json()
    @uplink.get("bulkchange/{bulk_id}")
    def get(self, bulk_id: uplink.Path) -> BulkChange:  # ty: ignore[empty-body]
        """``GET /bulkchange/{bulk_id}`` → the operation's current status (poll this to wait).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.get("1ab23cd4…").is_terminal  # doctest: +SKIP
            True
        """

    @uplink.returns.json()
    @uplink.get("bulkchange/{bulk_id}/issues")
    def issues(self, bulk_id: uplink.Path) -> BulkIssueResultList:  # ty: ignore[empty-body]
        """``GET /bulkchange/{bulk_id}/issues`` → issues for which the operation failed.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.bulk.issues("1ab23cd4…").root[0].issue  # doctest: +SKIP
            'TEST-1'
        """
