"""Tracker /queues FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, require_found
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueCreate,
    QueueFieldList,
    QueueList,
    QueuePermissions,
    QueuePermissionsUpdate,
    QueueTagList,
    QueueTagRemove,
    QueueVersionCreate,
    QueueVersionInfo,
    QueueVersionInfoList,
)

mcp = FastMCP("tracker-queues")


@mcp.tool(name="queues_list", annotations={**RO, "title": "List Tracker queues"}, tags=TAGS)
def list_(
    limit: Annotated[
        int, Field(description="Max queues to return; 0 uses the YCLI_MAX_ITEMS cap (default 500).")
    ] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> QueueList:
    """Every queue the caller can see, auto-paginated over the API's page/perPage pages.

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. Each item's ``key`` is the
    queue key (e.g. TEST) you pass to ``queues_get`` and use as an issue prefix (TEST-123). Use
    ``queues_get`` for a single queue's full configuration (types, workflows, resolutions).

    Example:
        >>> queues_list(limit=10)  # doctest: +SKIP
    """
    cap = resolve_cap(limit, config.max_items)
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
    return require_found(
        result,
        sentinel=lambda r: r.key is None and r.id is None,
        message=f"queue {queue_id!r} not found (got empty response — check key/id or permissions)",
    )


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

    These are the tags selectable on the queue's issues (the ``tags`` field). Remove one
    everywhere with ``queues_tag_remove``.

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

    Each item carries the version's name, date range and released/archived flags. Create one
    with ``queues_version_create``.

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


@mcp.tool(
    name="queues_create", annotations={**WRITE, "title": "Create Tracker queue"}, tags=WRITE_TAGS
)
def create(body: QueueCreate, client: TrackerClient = Depends(tracker_client)) -> Queue:
    """Create a Tracker queue (the container issues live in; its key prefixes issue keys).

    Required: ``key`` (latin, uppercase), ``name``, ``lead`` (login), ``default_type`` (issue
    type key, e.g. ``task``) and ``default_priority`` (priority key, e.g. ``normal``). Returns
    the new queue.
    """
    return client.queues.create(body)


@mcp.tool(
    name="queues_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker queue"},
    tags=WRITE_TAGS,
)
def delete(queue_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Delete a Tracker queue WITH ALL ITS ISSUES (recoverable via ``queues_restore``).

    The queue moves to the recycle bin and can be restored for a limited time. Returns an
    acknowledgement on success.
    """
    client.queues.delete(queue_id)
    return Ack.deleted("queue", queue_id)


@mcp.tool(
    name="queues_restore", annotations={**WRITE, "title": "Restore Tracker queue"}, tags=WRITE_TAGS
)
def restore(queue_id: str, client: TrackerClient = Depends(tracker_client)) -> Queue:
    """Restore a previously deleted Tracker queue (and its issues) from the recycle bin.

    Returns the restored queue.
    """
    return client.queues.restore(queue_id)


@mcp.tool(
    name="queues_set_permissions",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Tracker queue permissions"},
    tags=WRITE_TAGS,
)
def set_permissions(
    queue_id: str, body: QueuePermissionsUpdate, client: TrackerClient = Depends(tracker_client)
) -> QueuePermissions:
    """Replace access rules on a Tracker queue (grant/revoke read/write/create/grant rights).

    Each right block takes ``users``/``groups``/``roles`` arrays; omitted blocks stay
    unchanged. Returns the resulting permission set.
    """
    return client.queues.set_permissions(queue_id, body)


@mcp.tool(
    name="queues_tag_remove",
    annotations={**DESTRUCTIVE, "title": "Remove Tracker queue tag"},
    tags=WRITE_TAGS,
)
def tag_remove(
    queue_id: str, body: QueueTagRemove, client: TrackerClient = Depends(tracker_client)
) -> Ack:
    """Remove a tag from EVERY issue of a queue (irreversible; the tag disappears queue-wide).

    ``body`` is ``{"tag": "<name>"}`` — pick the name from ``queues_tags_list``. Returns an
    acknowledgement on success.
    """
    client.queues.tag_remove(queue_id, body)
    return Ack.removed("tag", body.tag, from_=f"queue {queue_id}")


@mcp.tool(
    name="queues_version_create",
    annotations={**WRITE, "title": "Create Tracker queue version"},
    tags=WRITE_TAGS,
)
def version_create(
    body: QueueVersionCreate, client: TrackerClient = Depends(tracker_client)
) -> QueueVersionInfo:
    """Create a version (release milestone) on a queue.

    Required: ``queue`` (the queue key) and ``name``; optional ``description``,
    ``start_date`` / ``due_date`` (``YYYY-MM-DD``). Returns the new version.
    """
    return client.queues.version_create(body)
