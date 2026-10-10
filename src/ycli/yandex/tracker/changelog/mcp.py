"""Tracker changelog FastMCP tool (reads-only)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Listed, SortDirection
from ycli.yandex.tracker.changelog.models import ChangelogEntry
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    LIMIT_CAP,
    RO,
    All,
    IssueKey,
    Next,
    app_config,
    new_server,
    tracker_client,
)

mcp = new_server("tracker-changelog")


@mcp.tool(name="changelog_list", annotations={**RO, "title": "List Tracker issue changelog"})
def list_(
    issue_key: IssueKey,
    limit: Annotated[
        int | None,
        Field(ge=1, description=f"Max changes to return; {LIMIT_CAP}"),
    ] = None,
    all: All = False,
    next: Next = None,
    field: Annotated[
        str | None, Field(description="Keep the changes of this field, e.g. ``status``.")
    ] = None,
    change_type: Annotated[
        str | None, Field(description="Keep the changes of this type, e.g. ``IssueWorkflow``.")
    ] = None,
    sort: Annotated[SortDirection | None, Field(description="Order of the changes.")] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> Listed[ChangelogEntry]:
    """Full changelog (edit history) for a Tracker issue.

    Auto-paginated via the relative id-cursor. Capped at the configured item cap unless ``limit``
    is given.
    """
    cap = config.http.tool_cap(limit, all_=all)
    return client.changelog.list(
        issue_key, limit=cap, next=next, field=field, change_type=change_type, sort=sort
    ).collect()
