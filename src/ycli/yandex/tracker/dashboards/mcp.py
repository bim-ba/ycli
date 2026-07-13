"""Tracker dashboards FastMCP tools (writes, ARCH-3 honest annotations)."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dashboards.models import (
    CycleTimeWidget,
    Dashboard,
    DashboardCreate,
    Widget,
)
from ycli.yandex.tracker.dependencies import WRITE, WRITE_TAGS, tracker_client

mcp = FastMCP("tracker-dashboards")


@mcp.tool(
    name="dashboards_create",
    annotations={**WRITE, "title": "Create Tracker dashboard"},
    tags=WRITE_TAGS,
)
def create(body: DashboardCreate, client: TrackerClient = Depends(tracker_client)) -> Dashboard:
    """Create a personal Tracker dashboard; returns it with the id used to add widgets.

    NOTE: dashboard deletion is not wrapped by ycli, so the dashboard stays on the account
    until removed in the UI.
    """
    return client.dashboards.create(body.model_dump(by_alias=True, exclude_none=True))


@mcp.tool(
    name="dashboards_add_cycle_time_widget",
    annotations={**WRITE, "title": "Add Tracker cycle-time widget"},
    tags=WRITE_TAGS,
)
def add_cycle_time_widget(
    dashboard_id: str, body: CycleTimeWidget, client: TrackerClient = Depends(tracker_client)
) -> Widget:
    """Add a cycle-time widget to a Tracker dashboard; returns the created widget.

    Get ``dashboard_id`` from ``dashboards_create``.
    """
    return client.dashboards.add_cycle_time_widget(
        dashboard_id, body.model_dump(by_alias=True, exclude_none=True)
    )
