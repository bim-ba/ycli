"""Declarative Tracker issue-transitions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.transitions.models import TransitionList


class TransitionsClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/transitions``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/transitions")
    def list(self, key: uplink.Path) -> TransitionList:  # ty: ignore[empty-body]
        """``GET /issues/{key}/transitions`` → available transitions.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.transitions.list(key="DATAENGINEERING-1").root[0].id  # doctest: +SKIP
            'start_progress'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{key}/transitions/{transition_id}/_execute")
    def execute(
        self, key: uplink.Path, transition_id: uplink.Path, body: uplink.Body
    ) -> TransitionList:  # ty: ignore[empty-body]
        """``POST /issues/{key}/transitions/{id}/_execute`` → available transitions after move.

        Returns the transitions available for the issue in its new status,
        parsed as a ``TransitionList``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> result = client.transitions.execute("DE-1", "start_progress", {})  # doctest: +SKIP
            >>> result.root[0].id  # doctest: +SKIP
            'stop_progress'
        """
