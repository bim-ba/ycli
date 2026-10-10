"""Tracker /queues FastMCP tools (reads + writes, ARCH-3 honest annotations)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList, Listed
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    GRANTS_ACCESS,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    All,
    Expand,
    Next,
    QueueID,
    app_config,
    new_server,
    tracker_client,
)
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueCreate,
    QueueField,
    QueueGroupAccess,
    QueuePermissions,
    QueuePermissionsUpdate,
    QueueTagRemove,
    QueueUserAccess,
    QueueVersionCreate,
    QueueVersionInfo,
    QueueVersionUpdate,
)

mcp = new_server("tracker-queues")


@mcp.tool(name="queues_list", annotations={**RO, "title": "List Tracker queues"})
def list_(
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max queues to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    expand: Expand = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Queue]:
    """Every queue the caller can see, auto-paginated over the API's page/perPage pages.

    Capped at the configured item cap unless ``limit`` is given. Each item's ``key`` is the
    queue key (e.g. TEST) you pass to ``queues_get`` and use as an issue prefix (TEST-123). Use
    ``queues_get`` for a single queue's full configuration (types, workflows, resolutions).
    """
    cap = config.http.tool_cap(limit, all_=all)
    return client.queues.list(limit=cap, next=next, expand=expand).collect()


@mcp.tool(name="queues_get", annotations={**RO, "title": "Get Tracker queue"})
def get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    expand: Annotated[
        str | None,
        Field(
            description=(
                "Extra blocks to include, e.g. 'all' or a comma list of "
                "projects,components,versions,types,team,workflows,fields,issueTypesConfig."
            )
        ),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Queue:
    """One queue's settings and configuration by key or id.

    Returns the queue's owner, default type/priority, and — when ``expand`` is set — its issue
    types, versions, team, workflows and per-type resolution config. Sibling ``queues_list``
    enumerates every queue; pass one of its ``key`` values here.
    """
    return client.queues.get(queue_id, expand=expand)


@mcp.tool(name="queues_tags_list", annotations={**RO, "title": "List Tracker queue tags"})
def tags_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[str]:
    """Every tag name that has been added to the queue, as a flat string array.

    These are the tags selectable on the queue's issues (the ``tags`` field). Remove one
    everywhere with ``queues_tags_delete``.
    """
    return client.queues.tags_list(queue_id)


@mcp.tool(
    name="queues_versions_list",
    annotations={**RO, "title": "List Tracker queue versions"},
)
def versions_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[QueueVersionInfo]:
    """The queue's versions — release milestones issues can be assigned to.

    Each item carries the version's name, date range and released/archived flags. Create one
    with ``queues_versions_create``.
    """
    return client.queues.versions_list(queue_id)


@mcp.tool(
    name="queues_fields_list",
    annotations={**RO, "title": "List Tracker queue required fields"},
)
def fields_list(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[QueueField]:
    """The queue's required/local fields with their schema, options and display order.

    Use this to learn which fields an issue in the queue expects (and whether each is required)
    before creating or updating issues there.
    """
    return client.queues.fields_list(queue_id)


@mcp.tool(name="queues_create", annotations={**WRITE, "title": "Create Tracker queue"})
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
)
def delete(queue_id: QueueID, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Delete a Tracker queue WITH ALL ITS ISSUES (recoverable via ``queues_restore``).

    The queue moves to the recycle bin and can be restored for a limited time. Returns an
    acknowledgement on success.
    """
    client.queues.delete(queue_id)
    return Ack.deleted("queue", queue_id)


@mcp.tool(name="queues_restore", annotations={**WRITE, "title": "Restore Tracker queue"})
def restore(queue_id: QueueID, client: TrackerClient = Depends(tracker_client)) -> Queue:
    """Restore a previously deleted Tracker queue (and its issues) from the recycle bin.

    Returns the restored queue.
    """
    return client.queues.restore(queue_id)


@mcp.tool(
    name="queues_permissions_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Tracker queue permissions"},
    meta=GRANTS_ACCESS,
)
def permissions_update(
    queue_id: QueueID, body: QueuePermissionsUpdate, client: TrackerClient = Depends(tracker_client)
) -> QueuePermissions:
    """Replace access rules on a Tracker queue (grant/revoke read/write/create/grant rights).

    Each right block takes ``users``/``groups``/``roles`` arrays; omitted blocks stay
    unchanged. Returns the resulting permission set. A removal is not always the inverse of an
    addition: taking a user out of ``read`` took it out of ``write`` too (seen once,
    2026-10-06), so read the returned set after a removal. Adding a member that is there
    already changes nothing.
    """
    return client.queues.permissions_update(queue_id, body)


@mcp.tool(
    name="queues_tags_delete",
    annotations={**DESTRUCTIVE, "title": "Remove Tracker queue tag"},
)
def tags_delete(
    queue_id: QueueID, body: QueueTagRemove, client: TrackerClient = Depends(tracker_client)
) -> Ack:
    """Remove a tag from EVERY issue of a queue (irreversible; the tag disappears queue-wide).

    ``body`` is ``{"tag": "<name>"}`` — pick the name from ``queues_tags_list``. Returns an
    acknowledgement on success.
    """
    client.queues.tags_delete(queue_id, body)
    return Ack.removed("tag", body.tag, from_=f"queue {queue_id}")


@mcp.tool(
    name="queues_versions_create",
    annotations={**WRITE, "title": "Create Tracker queue version"},
)
def versions_create(
    body: QueueVersionCreate, client: TrackerClient = Depends(tracker_client)
) -> QueueVersionInfo:
    """Create a version (release milestone) on a queue.

    Required: ``queue`` (the queue key) and ``name``; optional ``description``,
    ``start_date`` / ``due_date`` (``YYYY-MM-DD``). Returns the new version.
    """
    return client.queues.versions_create(body)


@mcp.tool(name="queues_versions_get", annotations={**RO, "title": "Get Tracker queue version"})
def versions_get(
    version_id: Annotated[
        int, Field(description="Numeric id of the version, from ``queues_versions_list``.")
    ],
    fields: Annotated[
        str | None,
        Field(description="Comma-separated fields to return, e.g. ``name,dueDate,released``."),
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> QueueVersionInfo:
    """One queue version: name, description, dates and its released/archived flags."""
    return client.queues.versions_get(version_id, fields=fields)


@mcp.tool(
    name="queues_versions_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker queue version"},
)
def versions_update(
    version_id: Annotated[
        int, Field(description="Numeric id of the version, from ``queues_versions_list``.")
    ],
    body: QueueVersionUpdate,
    fields: Annotated[
        str | None, Field(description="Comma-separated fields to return in the reply.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> QueueVersionInfo:
    """Edit a queue version; only the fields set in ``body`` change. Returns the version."""
    return client.queues.versions_update(version_id, body, fields=fields)


@mcp.tool(
    name="queues_versions_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker queue version"},
)
def versions_delete(
    version_id: Annotated[
        int, Field(description="Numeric id of the version, from ``queues_versions_list``.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete a queue version (irreversible). Returns an acknowledgement."""
    client.queues.versions_delete(version_id)
    return Ack.deleted("version", version_id)


@mcp.tool(
    name="queues_user_permissions_get",
    annotations={**RO, "title": "Get a user's rights in a Tracker queue"},
)
def user_permissions_get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    user_id: Annotated[str, Field(description="Login or numeric uid of the user.")],
    client: TrackerClient = Depends(tracker_client),
) -> QueueUserAccess:
    """What one user may do in a queue (create, read, write, grant, deny) and why.

    Each right lists who grants it: the user personally, a group or a role. To change rights
    use ``queues_permissions_update``.
    """
    return client.queues.user_permissions_get(queue_id, user_id)


@mcp.tool(
    name="queues_group_permissions_get",
    annotations={**RO, "title": "Get a group's rights in a Tracker queue"},
)
def group_permissions_get(
    queue_id: Annotated[
        str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
    ],
    group_id: Annotated[int, Field(description="Numeric id of the group.")],
    client: TrackerClient = Depends(tracker_client),
) -> QueueGroupAccess:
    """What one group may do in a queue (create, read, write, grant, deny)."""
    return client.queues.group_permissions_get(queue_id, group_id)
