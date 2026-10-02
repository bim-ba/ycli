"""Tracker ``/dashboards`` client on the httpx2 core: create a dashboard, add a cycle-time widget.

Every method sends one declaration from :mod:`ycli.yandex.tracker.dashboards.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.dashboards import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.dashboards.models import Dashboard, Widget


class DashboardsClient(Resource):
    """``/dashboards`` (create a dashboard, add a cycle-time widget)."""

    def create(self, body: dict[str, Any]) -> Dashboard:
        """``POST /dashboards/`` — create a dashboard. Returns the created ``Dashboard``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.dashboards.create({"name": "Team board"}).id  # doctest: +SKIP
            10
        """
        return self._session.send(endpoints.create_dashboard(body))

    def add_cycle_time_widget(self, dashboard_id: str, body: dict[str, Any]) -> Widget:
        """``POST /dashboards/{dashboard_id}/widgets/cycleTime`` — add a cycle-time widget.

        Returns the created ``Widget``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.dashboards.add_cycle_time_widget(
            ...     10, {"description": "My widget", "query": "Queue: TEST"}
            ... ).id  # doctest: +SKIP
            123456
        """
        return self._session.send(endpoints.add_cycle_time_widget(dashboard_id, body))
