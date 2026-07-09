"""Declarative Tracker sprints client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.sprints.models import Sprint, SprintCreate, SprintList, SprintUpdate


class SprintsClient(TrackerResource):
    """Declarative HTTP for board ``/sprints`` (list per board + get by id)."""

    @uplink.returns.json()
    @uplink.get("boards/{board_id}/sprints")
    def list(self, board_id: uplink.Path) -> SprintList:  # ty: ignore[empty-body]
        """``GET /boards/{board_id}/sprints`` → the board's sprint listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.list(board_id=3).root[0].name  # doctest: +SKIP
            'Sprint 1'
        """

    @uplink.returns.json()
    @uplink.get("sprints/{sprint_id}")
    def get(self, sprint_id: uplink.Path) -> Sprint:  # ty: ignore[empty-body]
        """``GET /sprints/{sprint_id}`` → a single sprint.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.get(sprint_id=4405).status  # doctest: +SKIP
            'in_progress'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("sprints")
    def _create(self, body: uplink.Body) -> Sprint:  # ty: ignore[empty-body]
        """``POST /sprints`` — create a sprint from a ready JSON body (see ``create``)."""

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
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("sprints/{sprint_id}")
    def _edit(self, sprint_id: uplink.Path, body: uplink.Body) -> Sprint:  # ty: ignore[empty-body]
        """``PATCH /sprints/{sprint_id}`` — edit a sprint from a ready JSON body (see ``edit``)."""

    def edit(self, sprint_id: int, body: SprintUpdate) -> Sprint:
        """Edit a sprint from a typed ``SprintUpdate`` body. Returns the updated ``Sprint``.

        Only the fields set on ``body`` are sent, so omitted fields stay unchanged.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.edit(4405, SprintUpdate(name="Updated")).name  # doctest: +SKIP
            'Updated'
        """
        return self._edit(
            sprint_id=sprint_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.delete("sprints/{sprint_id}")
    def delete(self, sprint_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /sprints/{sprint_id}`` — delete a sprint (``204``, empty body).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.delete(sprint_id=4405).status_code  # doctest: +SKIP
            204
        """

    @uplink.returns.json()
    @uplink.post("sprints/{sprint_id}/_start")
    def start(self, sprint_id: uplink.Path) -> Sprint:  # ty: ignore[empty-body]
        """``POST /sprints/{sprint_id}/_start`` — start a sprint (status → in_progress).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.start(sprint_id=4405).status  # doctest: +SKIP
            'in_progress'
        """

    @uplink.returns.json()
    @uplink.post("sprints/{sprint_id}/_archive")
    def archive(self, sprint_id: uplink.Path) -> Sprint:  # ty: ignore[empty-body]
        """``POST /sprints/{sprint_id}/_archive`` — archive a sprint (status → archived).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.sprints.archive(sprint_id=4405).status  # doctest: +SKIP
            'archived'
        """
