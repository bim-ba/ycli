"""Tracker changelog FastMCP tool (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.changelog.models import ChangelogList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, app_config, tracker_client

mcp = FastMCP("tracker-changelog")


@mcp.tool(
    name="changelog_list", annotations={**RO, "title": "List Tracker issue changelog"}, tags=TAGS
)
def list_(
    key: str,
    limit: Annotated[
        int,
        Field(description="Max changes to return; 0 means the YCLI_MAX_ITEMS cap (default 500)."),
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
    cfg: AppConfig = Depends(app_config),
) -> ChangelogList:
    """Full changelog (edit history) for a Tracker issue, auto-paginated via the relative
    id-cursor. Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given.
    """
    cap = resolve_cap(limit, cfg.max_items)
    return client.changelog.list(key, limit=cap)
