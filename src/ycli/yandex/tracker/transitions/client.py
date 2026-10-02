"""Tracker issue ``/transitions`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.transitions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.transitions.models import TransitionList


class TransitionsClient(Resource):
    """List an issue's workflow transitions and execute one."""

    def list(self, key: str) -> TransitionList:
        """``GET /issues/{key}/transitions`` → available transitions.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.transitions.list(key="DATAENGINEERING-1").root[0].id  # doctest: +SKIP
            'start_progress'
        """
        return self._session.send(endpoints.list_transitions(key))

    def execute(self, key: str, transition_id: str, body: dict[str, Any]) -> TransitionList:
        """``POST /issues/{key}/transitions/{id}/_execute`` → available transitions after move.

        Returns the transitions available for the issue in its new status,
        parsed as a ``TransitionList``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> result = client.transitions.execute("DE-1", "start_progress", {})  # doctest: +SKIP
            >>> result.root[0].id  # doctest: +SKIP
            'stop_progress'
        """
        return self._session.send(endpoints.execute_transition(key, transition_id, body))
