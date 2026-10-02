"""Tracker ``/sprints`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.sprints import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.sprints.models import Sprint, SprintCreate, SprintList, SprintUpdate


class SprintsClient(Resource):
    """List a board's sprints; get, create, edit, delete, start and archive a sprint."""

    def list(self, board_id: int) -> SprintList:
        """``GET /boards/{board_id}/sprints`` → the board's sprint listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.list(board_id=3).root[0].name  # doctest: +SKIP
            'Sprint 1'
        """
        return self._session.send(endpoints.list_sprints(board_id))

    def get(self, sprint_id: int) -> Sprint:
        """``GET /sprints/{sprint_id}`` → a single sprint.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.get(sprint_id=4405).status  # doctest: +SKIP
            'in_progress'
        """
        return self._session.send(endpoints.get_sprint(sprint_id))

    def create(self, body: SprintCreate) -> Sprint:
        """Create a sprint from a typed ``SprintCreate`` body. Returns the created ``Sprint``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.create(
            ...     SprintCreate(
            ...         name="New Sprint",
            ...         board=SprintBoardInput(id="1"),
            ...         start_date="2018-10-21",
            ...         end_date="2018-10-24",
            ...     )
            ... ).id  # doctest: +SKIP
            4405
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_sprint(dumped))

    def edit(self, sprint_id: int, body: SprintUpdate, *, version: int | None = None) -> Sprint:
        """Edit a sprint from a typed ``SprintUpdate`` body. Returns the updated ``Sprint``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged. ``version``
        is the sprint's current version, sent as ``?version=`` — the API requires it (or an
        ``If-Match`` header) for optimistic locking and answers 428 without one.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.edit(
            ...     4405, SprintUpdate(name="Updated"), version=1
            ... ).name  # doctest: +SKIP
            'Updated'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.edit_sprint(sprint_id, dumped, version))

    def delete(self, sprint_id: int) -> None:
        """``DELETE /sprints/{sprint_id}`` — delete a sprint (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.delete(sprint_id=4405)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_sprint(sprint_id))

    def start(self, sprint_id: int, *, version: int | None = None) -> Sprint:
        """``POST /sprints/{sprint_id}/_start`` — start a sprint (status → in_progress).

        ``version`` is the sprint's current version, sent as ``?version=`` — the API requires
        it (or an ``If-Match`` header) for optimistic locking and answers 428 without one.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.start(sprint_id=4405, version=1).status  # doctest: +SKIP
            'in_progress'
        """
        return self._session.send(endpoints.start_sprint(sprint_id, version))

    def archive(self, sprint_id: int, *, version: int | None = None) -> Sprint:
        """``POST /sprints/{sprint_id}/_archive`` — archive a sprint (status → archived).

        ``version`` is the sprint's current version, sent as ``?version=`` — the API requires
        it (or an ``If-Match`` header) for optimistic locking and answers 428 without one.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.archive(sprint_id=4405, version=1).status  # doctest: +SKIP
            'archived'
        """
        return self._session.send(endpoints.archive_sprint(sprint_id, version))
