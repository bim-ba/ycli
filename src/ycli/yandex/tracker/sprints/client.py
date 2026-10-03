"""Tracker ``/sprints`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.sprints import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.sprints.models import Sprint, SprintCreate, SprintUpdate


class SprintsClient(Resource):
    """List a board's sprints; get, create, update, delete, start and archive a sprint."""

    def list(self, board_id: int) -> ItemList[Sprint]:
        """``GET /boards/{board_id}/sprints`` → the board's sprint listing.

        Args:
            board_id: The board's id.

        Returns:
            The board's sprints.

        Examples:
            >>> tracker.sprints.list(3).root[0].name
            'Sprint 1'
        """
        return self._session.send(endpoints.list_sprints(board_id))

    def get(self, sprint_id: int) -> Sprint:
        """``GET /sprints/{sprint_id}`` → a single sprint.

        Args:
            sprint_id: The sprint's id.

        Returns:
            The sprint.

        Examples:
            >>> tracker.sprints.get(4402).status
            'in_progress'
        """
        return self._session.send(endpoints.get_sprint(sprint_id))

    def create(self, body: SprintCreate) -> Sprint:
        """Create a sprint from a typed ``SprintCreate`` body. Returns the created ``Sprint``.

        Args:
            body: The new sprint's name, board and dates.

        Returns:
            The created sprint.

        Examples:
            >>> from ycli.yandex.tracker.sprints.models import SprintBoardInput, SprintCreate
            >>> new_sprint = SprintCreate(
            ...     name="Sprint 9",
            ...     board=SprintBoardInput(id="17"),
            ...     start_date="2026-10-05",
            ...     end_date="2026-10-19",
            ... )
            >>> tracker.sprints.create(new_sprint).id
            4403
        """
        return self._session.send(endpoints.create_sprint(body))

    def update(self, sprint_id: int, body: SprintUpdate, *, version: int | None = None) -> Sprint:
        """Edit a sprint from a typed ``SprintUpdate`` body. Returns the updated ``Sprint``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged. ``version``
        is the sprint's current version, sent as ``?version=`` — the API requires it (or an
        ``If-Match`` header) for optimistic locking and answers 428 without one.

        Args:
            sprint_id: The sprint's id.
            body: The fields to change.
            version: The sprint's current version, sent as ``?version=``.

        Returns:
            The updated sprint.

        Examples:
            >>> from ycli.yandex.tracker.sprints.models import SprintUpdate
            >>> tracker.sprints.update(4404, SprintUpdate(name="Updated"), version=5).name
            'Updated'
        """
        return self._session.send(endpoints.update_sprint(sprint_id, body, version))

    def delete(self, sprint_id: int) -> None:
        """``DELETE /sprints/{sprint_id}`` — delete a sprint (``204``, empty body).

        Args:
            sprint_id: The sprint's id.

        Examples:
            >>> tracker.sprints.delete(4406)
        """
        self._session.send(endpoints.delete_sprint(sprint_id))

    def start(self, sprint_id: int, *, version: int | None = None) -> Sprint:
        """``POST /sprints/{sprint_id}/_start`` — start a sprint (status → in_progress).

        ``version`` is the sprint's current version, sent as ``?version=`` — the API requires
        it (or an ``If-Match`` header) for optimistic locking and answers 428 without one.

        Args:
            sprint_id: The sprint's id.
            version: The sprint's current version, sent as ``?version=``.

        Returns:
            The started sprint.

        Examples:
            >>> tracker.sprints.start(4407, version=6).status
            'in_progress'
        """
        return self._session.send(endpoints.start_sprint(sprint_id, version))

    def archive(self, sprint_id: int, *, version: int | None = None) -> Sprint:
        """``POST /sprints/{sprint_id}/_archive`` — archive a sprint (status → archived).

        ``version`` is the sprint's current version, sent as ``?version=`` — the API requires
        it (or an ``If-Match`` header) for optimistic locking and answers 428 without one.

        Args:
            sprint_id: The sprint's id.
            version: The sprint's current version, sent as ``?version=``.

        Returns:
            The archived sprint.

        Examples:
            >>> tracker.sprints.archive(4409, version=7).status
            'archived'
        """
        return self._session.send(endpoints.archive_sprint(sprint_id, version))
