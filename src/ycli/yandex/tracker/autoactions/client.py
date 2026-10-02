"""Tracker queue ``/autoactions`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.autoactions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.autoactions.models import (
        Autoaction,
        AutoactionCreate,
        AutoactionLogList,
        AutoactionRunList,
    )


class AutoactionsClient(Resource):
    """Get and create a queue's autoactions; read their run logs."""

    def get(self, queue_id: str, action_id: int) -> Autoaction:
        """``GET /queues/{queue_id}/autoactions/{action_id}`` → a single autoaction.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.autoactions.get(queue_id="DESIGN", action_id=9).name  # doctest: +SKIP
            'autoaction_name'
        """
        return self._session.send(endpoints.get_autoaction(queue_id, action_id))

    def create(self, queue_id: str, body: AutoactionCreate) -> Autoaction:
        """Create an autoaction from a typed ``AutoactionCreate`` body. Returns the ``Autoaction``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.autoactions.create(
            ...     "DESIGN",
            ...     AutoactionCreate(
            ...         name="A",
            ...         query="Status: Open",
            ...         actions=[AutoactionAction(type="Transition")],
            ...     ),
            ... ).id  # doctest: +SKIP
            9
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_autoaction(queue_id, dumped))

    def logs(self, queue_id: str, action_id: int) -> AutoactionLogList:
        """``GET /queues/{queue_id}/autoactions/{action_id}/logs`` → per-run summaries.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.autoactions.logs("DESIGN", 9).root[0].search_hits  # doctest: +SKIP
            3
        """
        return self._session.send(endpoints.list_run_logs(queue_id, action_id))

    def log_detail(self, queue_id: str, action_id: int, run_id: str) -> AutoactionRunList:
        """``GET .../autoactions/{action_id}/logs/{run_id}`` → per-issue outcomes of one run.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.autoactions.log_detail("DESIGN", 9, "abc").root[
            ...     0
            ... ].status.value  # doctest: +SKIP
            'success'
        """
        return self._session.send(endpoints.get_run_log(queue_id, action_id, run_id))
