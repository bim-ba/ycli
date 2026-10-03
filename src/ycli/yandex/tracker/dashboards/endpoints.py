"""Tracker ``/dashboards`` operations, each declared once (sans-IO).

Examples:
    >>> add_cycle_time_widget("10", {"description": "Cycle"}).path
    'dashboards/10/widgets/cycleTime'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.dashboards.models import (
    CycleTimeWidget,
    Dashboard,
    DashboardCreate,
    Widget,
)


def create_dashboard(body: DashboardCreate) -> Endpoint[Dashboard]:
    return Endpoint("POST", "dashboards/", Dashboard, json=body)


def add_cycle_time_widget(dashboard_id: str, body: CycleTimeWidget) -> Endpoint[Widget]:
    path = f"dashboards/{segment(dashboard_id)}/widgets/cycleTime"
    return Endpoint("POST", path, Widget, json=body)
