"""Tracker issue ``/transitions`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.transitions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.transitions.models import Transition, TransitionExecute


class TransitionsClient(Resource):
    """List an issue's workflow transitions and execute one."""

    def list(self, issue_key: str) -> ItemList[Transition]:
        """``GET /issues/{key}/transitions`` → available transitions.

        Args:
            issue_key: The issue's key.

        Returns:
            The transitions available for the issue.

        Examples:
            >>> tracker.transitions.list("DE-51").root[0].id
            'close'
        """
        return self._session.send(endpoints.list_(issue_key))

    def execute(
        self, issue_key: str, transition_id: str, body: TransitionExecute
    ) -> ItemList[Transition]:
        """``POST /issues/{key}/transitions/{id}/_execute`` → available transitions after move.

        Returns the transitions available for the issue in its new status,
        parsed as a ``ItemList[Transition]``.

        Args:
            issue_key: The issue's key.
            transition_id: The id of the transition to execute.
            body: The transition's fields, such as ``comment`` or ``resolution``.

        Returns:
            The transitions available after the move.

        Examples:
            >>> from ycli.yandex.tracker.transitions.models import TransitionExecute
            >>> result = tracker.transitions.execute(
            ...     "DE-52",
            ...     "close",
            ...     TransitionExecute.model_validate({"comment": "done", "resolution": "fixed"}),
            ... )
            >>> result.root[0].id
            'reopen'
        """
        return self._session.send(endpoints.execute(issue_key, transition_id, body))
