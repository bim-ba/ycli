"""Tracker queue ``/autoactions`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.autoactions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.autoactions.models import (
        Autoaction,
        AutoactionCreate,
        AutoactionLogEntry,
        AutoactionRunEntry,
    )


class AutoactionsClient(Resource):
    """Get and create a queue's autoactions; read their run logs."""

    def get(self, queue_id: str, action_id: int) -> Autoaction:
        """``GET /queues/{queue_id}/autoactions/{action_id}`` → a single autoaction.

        Args:
            queue_id: The queue's key or id.
            action_id: The autoaction's id.

        Returns:
            The autoaction.

        Examples:
            >>> tracker.autoactions.get("DESIGN", 9).name
            'Nightly'
        """
        return self._session.send(endpoints.get_autoaction(queue_id, action_id))

    def create(self, queue_id: str, body: AutoactionCreate) -> Autoaction:
        """Create an autoaction from a typed ``AutoactionCreate`` body. Returns the ``Autoaction``.

        Args:
            queue_id: The queue's key or id.
            body: The new autoaction's settings.

        Returns:
            The created autoaction.

        Examples:
            >>> from ycli.yandex.tracker.autoactions.models import AutoactionCreate
            >>> from ycli.yandex.tracker.models import AutomationAction
            >>> tracker.autoactions.create(
            ...     "OPS",
            ...     AutoactionCreate(
            ...         name="Stale sweep",
            ...         query="Status: Open",
            ...         actions=[AutomationAction(type="Transition")],
            ...     ),
            ... ).id
            10
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_autoaction(queue_id, dumped))

    def logs(self, queue_id: str, action_id: int) -> ItemList[AutoactionLogEntry]:
        """``GET /queues/{queue_id}/autoactions/{action_id}/logs`` → per-run summaries.

        Args:
            queue_id: The queue's key or id.
            action_id: The autoaction's id.

        Returns:
            One summary per run.

        Examples:
            >>> tracker.autoactions.logs("QA", 11).root[0].search_hits
            3
        """
        return self._session.send(endpoints.list_run_logs(queue_id, action_id))

    def log_detail(
        self, queue_id: str, action_id: int, run_id: str
    ) -> ItemList[AutoactionRunEntry]:
        """``GET .../autoactions/{action_id}/logs/{run_id}`` → per-issue outcomes of one run.

        Args:
            queue_id: The queue's key or id.
            action_id: The autoaction's id.
            run_id: The run's id.

        Returns:
            The outcome for each issue the run touched.

        Examples:
            >>> tracker.autoactions.log_detail("SUP", 12, "run-2").root[0].status.value
            'success'
        """
        return self._session.send(endpoints.get_run_log(queue_id, action_id, run_id))
