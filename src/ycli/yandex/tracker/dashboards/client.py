"""Declarative Tracker dashboards client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.dashboards.models import Dashboard, Widget


class DashboardsClient(TrackerResource):
    """Declarative HTTP for ``/dashboards`` (create a dashboard, add a cycle-time widget)."""

    @uplink.returns.json()
    @uplink.json
    @uplink.post("dashboards/")
    def create(self, body: uplink.Body) -> Dashboard:  # ty: ignore[empty-body]
        """``POST /dashboards/`` — create a dashboard. Returns the created ``Dashboard``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.dashboards.create({"name": "Team board"}).id  # doctest: +SKIP
            10
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("dashboards/{dashboard_id}/widgets/cycleTime")
    def add_cycle_time_widget(self, dashboard_id: uplink.Path, body: uplink.Body) -> Widget:  # ty: ignore[empty-body]
        """``POST /dashboards/{dashboard_id}/widgets/cycleTime`` — add a cycle-time widget.

        Returns the created ``Widget``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.dashboards.add_cycle_time_widget(
            ...     10, {"description": "My widget", "query": "Queue: TEST"}
            ... ).id  # doctest: +SKIP
            123456
        """
