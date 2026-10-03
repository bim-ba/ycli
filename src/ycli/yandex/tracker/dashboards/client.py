"""Tracker ``/dashboards`` client on the httpx2 core: create a dashboard, add a cycle-time widget.

Every method sends one declaration from :mod:`ycli.yandex.tracker.dashboards.endpoints`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.dashboards import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.dashboards.models import (
        CycleTimeWidget,
        Dashboard,
        DashboardCreate,
        Widget,
    )


class DashboardsClient(Resource):
    """``/dashboards`` (create a dashboard, add a cycle-time widget)."""

    def create(self, body: DashboardCreate) -> Dashboard:
        """``POST /dashboards/`` — create a dashboard. Returns the created ``Dashboard``.

        Args:
            body: The new dashboard's settings.

        Returns:
            The created dashboard.

        Examples:
            >>> from ycli.yandex.tracker.dashboards.models import DashboardCreate
            >>> tracker.dashboards.create(
            ...     DashboardCreate.model_validate({"name": "Team board", "layout": "two-columns"})
            ... ).id
            10
        """
        return self._session.send(endpoints.create_dashboard(body))

    def add_cycle_time_widget(self, dashboard_id: str, body: CycleTimeWidget) -> Widget:
        """``POST /dashboards/{dashboard_id}/widgets/cycleTime`` — add a cycle-time widget.

        Returns the created ``Widget``.

        Args:
            dashboard_id: The dashboard's id.
            body: The widget's settings: its description, issue query and statuses.

        Returns:
            The created widget.

        Examples:
            >>> from ycli.yandex.tracker.dashboards.models import CycleTimeWidget
            >>> tracker.dashboards.add_cycle_time_widget(
            ...     "11",
            ...     CycleTimeWidget.model_validate(
            ...         {"description": "Cycle time", "query": "Queue: DE"}
            ...     ),
            ... ).id
            123456
        """
        return self._session.send(endpoints.add_cycle_time_widget(dashboard_id, body))
