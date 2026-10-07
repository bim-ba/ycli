"""Tracker dashboards FastMCP tools (writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dashboards.models import (
    CycleTimeWidget,
    Dashboard,
    DashboardCreate,
    Widget,
)
from ycli.yandex.tracker.dependencies import WRITE, new_server, tracker_client

mcp = new_server("tracker-dashboards")


@mcp.tool(
    name="dashboards_create",
    annotations={**WRITE, "title": "Create Tracker dashboard"},
)
def create(body: DashboardCreate, client: TrackerClient = Depends(tracker_client)) -> Dashboard:
    """Create a personal Tracker dashboard; returns it with the id used to add widgets.

    NOTE: dashboard deletion is not wrapped by ycli, so the dashboard stays on the account
    until removed in the UI.
    """
    return client.dashboards.create(body)


@mcp.tool(
    name="dashboards_widgets_create_cycle_time",
    annotations={**WRITE, "title": "Add Tracker cycle-time widget"},
)
def widgets_create_cycle_time(
    dashboard_id: Annotated[str, Field(description="Id of the dashboard to add the widget to.")],
    body: CycleTimeWidget,
    client: TrackerClient = Depends(tracker_client),
) -> Widget:
    """Add a cycle-time widget to a Tracker dashboard; returns the created widget.

    Get ``dashboard_id`` from ``dashboards_create``.
    """
    return client.dashboards.widgets_create_cycle_time(dashboard_id, body)
