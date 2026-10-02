"""Tracker changelog FastMCP tool (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.tracker.changelog.models import ChangelogList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import LIMIT_CAP, RO, TAGS, app_config, tracker_client

mcp = FastMCP("tracker-changelog")


@mcp.tool(
    name="changelog_list", annotations={**RO, "title": "List Tracker issue changelog"}, tags=TAGS
)
def list_(
    key: str,
    limit: Annotated[
        int,
        Field(description=f"Max changes to return; {LIMIT_CAP}"),
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ChangelogList:
    """Full changelog (edit history) for a Tracker issue, auto-paginated via the relative
    id-cursor. Capped at the configured item cap unless ``limit`` is given.
    """
    cap = config.http.cap(limit)
    return client.changelog.list(key, limit=cap)
