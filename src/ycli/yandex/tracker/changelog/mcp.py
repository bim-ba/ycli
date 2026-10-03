"""Tracker changelog FastMCP tool (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.changelog.models import ChangelogEntry
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    LIMIT_CAP,
    RO,
    TAGS,
    IssueKey,
    app_config,
    tracker_client,
)

mcp = FastMCP("tracker-changelog")


@mcp.tool(
    name="changelog_list", annotations={**RO, "title": "List Tracker issue changelog"}, tags=TAGS
)
def list_(
    key: IssueKey,
    limit: Annotated[
        int | None,
        Field(ge=1, description=f"Max changes to return; {LIMIT_CAP}"),
    ] = None,
    field: Annotated[
        str | None, Field(description="Keep the changes of this field, e.g. ``status``.")
    ] = None,
    change_type: Annotated[
        str | None, Field(description="Keep the changes of this type, e.g. ``IssueWorkflow``.")
    ] = None,
    sort: Annotated[
        str | None, Field(description="Order of the changes: ``asc`` or ``desc``.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[ChangelogEntry]:
    """Full changelog (edit history) for a Tracker issue.

    Auto-paginated via the relative id-cursor. Capped at the configured item cap unless ``limit``
    is given.
    """
    cap = config.http.cap(limit)
    return client.changelog.list(key, limit=cap, field=field, change_type=change_type, sort=sort)
