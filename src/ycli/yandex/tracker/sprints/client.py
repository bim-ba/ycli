"""Declarative Tracker sprints client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.sprints.models import Sprint, SprintList


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
