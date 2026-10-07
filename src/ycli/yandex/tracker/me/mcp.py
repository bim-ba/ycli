"""Tracker /myself FastMCP tool (reads-only) — Depends DI."""

from fastmcp.dependencies import Depends

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, new_server, tracker_client
from ycli.yandex.tracker.me.models import Me

mcp = new_server("tracker-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Tracker user"})
def get(client: TrackerClient = Depends(tracker_client)) -> Me:
    """The authenticated Yandex Tracker user (a safe auth probe)."""
    return client.me.get()
