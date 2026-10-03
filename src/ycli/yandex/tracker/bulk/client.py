"""Tracker bulk-change client on the httpx2 core.

Every method sends one declaration from :mod:`ycli.yandex.tracker.bulk.endpoints`. The three
trigger calls (update/move/transition) each start an *async* operation and return a
:class:`~ycli.yandex.tracker.bulk.models.BulkChange`; the reads (:meth:`get`, :meth:`issues_list`)
let a caller poll it to a terminal state.
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
        BulkMove,
        BulkTransition,
        BulkUpdate,
    )


class BulkClient(Resource):
    """``/bulkchange`` (mass update/move/transition + status reads)."""

    def update(
        self,
        body: BulkUpdate,
        *,
        notify: bool | None = None,
    ) -> BulkChange:
        """``POST /bulkchange/_update`` — mass-edit issues. Returns the started ``BulkChange``.

        Args:
            body: The request body: the issues to change and the field values to set.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).

        Returns:
            The started bulk change.

        Examples:
            >>> from ycli.yandex.tracker.bulk.models import BulkUpdate
            >>> tracker.bulk.update(
            ...     BulkUpdate.model_validate(
            ...         {"issues": ["DE-1", "DE-2"], "values": {"priority": "minor"}}
            ...     )
            ... ).status
            'CREATED'
        """
        return self._session.send(endpoints.update_bulk(body, notify=notify))

    def move(
        self,
        body: BulkMove,
        *,
        notify: bool | None = None,
    ) -> BulkChange:
        """``POST /bulkchange/_move`` — mass-move issues to another queue. Returns a ``BulkChange``.

        Args:
            body: The request body: the target queue and the issues to move.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).

        Returns:
            The started bulk change.

        Examples:
            >>> from ycli.yandex.tracker.bulk.models import BulkMove
            >>> tracker.bulk.move(
            ...     BulkMove.model_validate({"queue": "CHECK", "issues": ["DE-3"]})
            ... ).id
            '2cd'
        """
        return self._session.send(endpoints.move_bulk(body, notify=notify))

    def transition(
        self,
        body: BulkTransition,
        *,
        notify: bool | None = None,
    ) -> BulkChange:
        """``POST /bulkchange/_transition`` — mass status transition. Returns a ``BulkChange``.

        Args:
            body: The request body: the transition to run and the issues to run it on.
            notify: Whether to notify the users in the issues' fields; ``None`` leaves the API's
                default (it notifies).

        Returns:
            The started bulk change.

        Examples:
            >>> from ycli.yandex.tracker.bulk.models import BulkTransition
            >>> tracker.bulk.transition(
            ...     BulkTransition.model_validate({"transition": "close", "issues": ["DE-4"]})
            ... ).status
            'CREATED'
        """
        return self._session.send(endpoints.transition_bulk(body, notify=notify))

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
        return self._session.send(endpoints.get_bulk(bulk_id))

    def issues_list(self, bulk_id: str) -> ItemList[BulkIssueResult]:
        """``GET /bulkchange/{bulk_id}/issues`` → issues for which the operation failed.

        Args:
            bulk_id: The bulk change's id.

        Returns:
            The per-issue results.

        Examples:
            >>> tracker.bulk.issues_list("5ij").root[0].issue
            'DE-9'
        """
        return self._session.send(endpoints.list_bulk_issues(bulk_id))
