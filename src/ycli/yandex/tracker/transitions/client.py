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

        Args:
            key: The issue's key.

        Returns:
            The transitions available for the issue.

        Examples:
            >>> tracker.transitions.list("DE-51").root[0].id
            'close'
        """
        return self._session.send(endpoints.list_transitions(key))

    def execute(self, key: str, transition_id: str, body: dict[str, Any]) -> TransitionList:
        """``POST /issues/{key}/transitions/{id}/_execute`` → available transitions after move.

        Returns the transitions available for the issue in its new status,
        parsed as a ``TransitionList``.

        Args:
            key: The issue's key.
            transition_id: The id of the transition to execute.
            body: The transition's fields, such as ``comment`` or ``resolution``.

        Returns:
            The transitions available after the move.

        Examples:
            >>> result = tracker.transitions.execute(
            ...     "DE-52", "close", {"comment": "done", "resolution": "fixed"}
            ... )
            >>> result.root[0].id
            'reopen'
        """
        return self._session.send(endpoints.execute_transition(key, transition_id, body))
