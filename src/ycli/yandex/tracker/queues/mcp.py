"""Tracker /queues FastMCP tools (reads-only)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, app_config, tracker_client
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueFieldList,
    QueueList,
    QueueTagList,
    QueueVersionInfoList,
)

mcp = FastMCP("tracker-queues")


@mcp.tool(name="queues_list", annotations={**RO, "title": "List Tracker queues"}, tags=TAGS)
def list_(
    limit: Annotated[
        int, Field(description="Max queues to return; 0 uses the YCLI_MAX_ITEMS cap (default 500).")
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
    cfg: AppConfig = Depends(app_config),
) -> QueueList:
    """Every queue the caller can see, auto-paginated over the API's page/perPage pages.

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. Each item's ``key`` is the
    queue key (e.g. TEST) you pass to ``queues_get`` and use as an issue prefix (TEST-123). Use
    ``queues_get`` for a single queue's full configuration (types, workflows, resolutions).

    Example:
        >>> queues_list(limit=10)  # doctest: +SKIP
    """
    cap = limit or cfg.max_items
    return client.queues.list(limit=cap)


@mcp.tool(name="queues_get", annotations={**RO, "title": "Get Tracker queue"}, tags=TAGS)
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    expand: Annotated[
        str,
        Field(
            description=(
                "Extra blocks to include, e.g. 'all' or a comma list of "
                "projects,components,versions,types,team,workflows,fields,issueTypesConfig."
            )
        ),
    ] = "",
    client: TrackerClient = Depends(tracker_client),
) -> Queue:
    """One queue's settings and configuration by key or id (raises if not found).

    Returns the queue's owner, default type/priority, and — when ``expand`` is set — its issue
    types, versions, team, workflows and per-type resolution config. Sibling ``queues_list``
    enumerates every queue; pass one of its ``key`` values here.

    Example:
        >>> queues_get("TEST", expand="all")  # doctest: +SKIP
    """
    result = client.queues.get(queue_id, expand=expand or None)
    if result.key is None and result.id is None:
        raise ValueError(
            f"queue {queue_id!r} not found (got empty response — check key/id or permissions)"
        )
    return result


@mcp.tool(
    name="queues_tags_list", annotations={**RO, "title": "List Tracker queue tags"}, tags=TAGS
)
def tags_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> QueueTagList:
    """Every tag name that has been added to the queue, as a flat string array.

    These are the tags selectable on the queue's issues (the ``tags`` field). Removing a tag is
    a write, so it lives on the CLI/SDK (``queues tag-remove``), not here.

    Example:
        >>> queues_tags_list("TEST")  # doctest: +SKIP
    """
    return client.queues.tags(queue_id)


@mcp.tool(
    name="queues_versions_list",
    annotations={**RO, "title": "List Tracker queue versions"},
    tags=TAGS,
)
def versions_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> QueueVersionInfoList:
    """The queue's versions — release milestones issues can be assigned to.

    Each item carries the version's name, date range and released/archived flags. Creating a
    version is a write (``queues version-create`` on the CLI/SDK).

    Example:
        >>> queues_versions_list("TEST")  # doctest: +SKIP
    """
    return client.queues.versions(queue_id)


@mcp.tool(
    name="queues_fields_list",
    annotations={**RO, "title": "List Tracker queue required fields"},
    tags=TAGS,
)
def fields_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> QueueFieldList:
    """The queue's required/local fields with their schema, options and display order.

    Use this to learn which fields an issue in the queue expects (and whether each is required)
    before creating or updating issues there.

    Example:
        >>> queues_fields_list("TEST")  # doctest: +SKIP
    """
    return client.queues.fields(queue_id)
