"""Declarative Tracker queue autoactions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.autoactions.models import (
    Autoaction,
    AutoactionCreate,
    AutoactionLogList,
    AutoactionRunList,
)
from ycli.yandex.tracker.base import TrackerResource


class AutoactionsClient(TrackerResource):
    """Declarative HTTP for a queue's ``/autoactions`` (get, create, run logs)."""

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/autoactions/{action_id}")
    def get(self, queue_id: uplink.Path, action_id: uplink.Path) -> Autoaction:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/autoactions/{action_id}`` → a single autoaction.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.autoactions.get(queue_id="DESIGN", action_id=9).name  # doctest: +SKIP
            'autoaction_name'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("queues/{queue_id}/autoactions")
    def _create(self, queue_id: uplink.Path, body: uplink.Body) -> Autoaction:  # ty: ignore[empty-body]
        """``POST /queues/{queue_id}/autoactions`` from a ready JSON body (see ``create``)."""

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
        return self._create(
            queue_id=queue_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/autoactions/{action_id}/logs")
    def logs(self, queue_id: uplink.Path, action_id: uplink.Path) -> AutoactionLogList:  # ty: ignore[empty-body]
        """``GET /queues/{queue_id}/autoactions/{action_id}/logs`` → per-run summaries.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.autoactions.logs("DESIGN", 9).root[0].search_hits  # doctest: +SKIP
            3
        """

    @uplink.returns.json()
    @uplink.get("queues/{queue_id}/autoactions/{action_id}/logs/{run_id}")
    def log_detail(
        self, queue_id: uplink.Path, action_id: uplink.Path, run_id: uplink.Path
    ) -> AutoactionRunList:  # ty: ignore[empty-body]
        """``GET .../autoactions/{action_id}/logs/{run_id}`` → per-issue outcomes of one run.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.autoactions.log_detail("DESIGN", 9, "abc").root[
            ...     0
            ... ].status.value  # doctest: +SKIP
            'success'
        """
