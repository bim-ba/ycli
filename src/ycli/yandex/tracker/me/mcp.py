"""Tracker /myself FastMCP tool (reads-only) — Depends DI."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.me.models import Me

mcp = FastMCP("tracker-me")


@mcp.tool(name="me_get", annotations={**RO, "title": "Get current Tracker user"}, tags=TAGS)
def get(client: TrackerClient = Depends(tracker_client)) -> Me:  # noqa: B008 — FastMCP resolves Depends at call time, not definition time
    """The authenticated Yandex Tracker user (a safe auth probe)."""
    result = client.me.get()
    if result.login is None:
        raise ValueError("auth probe failed — empty user (check YANDEX_ID_OAUTH_TOKEN)")
    return result
