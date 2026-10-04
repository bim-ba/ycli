"""Tracker Entities FastMCP tools (projects / portfolios / goals) — reads + writes.

Mirrors the SDK with honest ARCH-3 annotations: entity CRUD, comments, checklists, links,
attachments, permissions and bulk change. Only the binary attachment download stays CLI/SDK-only
(a base64 blob is not a useful MCP payload) — its ``…_list`` / ``…_get`` metadata siblings are
the MCP entry points; attaching also needs a ``temp_file_id`` from the (unwrapped) upload
endpoint.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    AddToFollowers,
    Expand,
    Notify,
    NotifyAuthor,
    ReplyFields,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.entities.models import (
    Acl,
    Attachment,
    BulkChangeOperation,
    BulkChangeUpdate,
    ChecklistItemInput,
    ChecklistMove,
    Comment,
    CommentUpdate,
    DirectPermissionsUpdate,
    Entity,
    EntityCreate,
    EntityEvent,
    EntitySearch,
    EntityUpdate,
    ExtendedPermissions,
    Link,
    LinkInput,
    PermissionsUpdate,
    ReportCreate,
)
from ycli.yandex.tracker.models import CommentCreate

mcp = FastMCP("tracker-entities")

TypeArg = Annotated[str, Field(description="Entity type: ``project``, ``portfolio`` or ``goal``.")]
SearchTypeArg = Annotated[
    str,
    Field(
        description="Entity type: ``project``, ``portfolio``, ``goal`` or ``report`` "
        "(issue reports)."
    ),
]
IdArg = Annotated[str, Field(description="Entity id (or shortId).")]


ChecklistItems = Annotated[
    ItemList[ChecklistItemInput], Field(description="A bare array of checklist items.")
]


@mcp.tool(name="entities_get", annotations={**RO, "title": "Get Tracker entity"})
def get(
    entity_type: TypeArg,
    entity_id: IdArg,
    fields: Annotated[
        str | None,
        Field(description="Comma-separated extra fields, e.g. ``keyResultItems,checklistItems``."),
    ] = None,
    expand: Annotated[str | None, Field(description="Extra info, e.g. ``attachments``.")] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """A single Tracker entity (project, portfolio or goal) by id, with its ``fields`` block.

    Pass ``fields`` to pull extra parameters into the response — ``keyResultItems`` for a goal's
    key results, ``checklistItems`` for a project/portfolio checklist, ``metricItems`` for its
    metric widgets, or ``summary,description,entityStatus`` for the basics. Use
    ``entities_search`` to discover ids first.
    """
    return client.entities.get(entity_type, entity_id, expand=expand, fields=fields)


@mcp.tool(name="entities_search", annotations={**RO, "title": "Search Tracker entities"})
def search(
    entity_type: SearchTypeArg,
    input_text: Annotated[
        str | None, Field(description="Substring to match in the entity name.")
    ] = None,
    order_by: Annotated[str | None, Field(description="Field key to sort the results by.")] = None,
    fields: Annotated[
        str | None, Field(description="Comma-separated extra fields to include.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> ItemList[Entity]:
    """Entities of a given type matching a name substring, sorted server-side.

    Returns a flat list of entities. Pass ``input_text`` to match part of the name and
    ``order_by`` (e.g. ``entityStatus``) to sort. For richer filtering (by author, status,
    followers, …) use the CLI ``tracker entities search --filter`` which accepts an arbitrary
    filter object.
    """
    body = EntitySearch.model_validate({"input": input_text, "orderBy": order_by})
    return client.entities.search(entity_type, body, fields=fields)


@mcp.tool(
    name="entities_events_list",
    annotations={**RO, "title": "List Tracker entity history"},
)
def events_list(
    entity_type: TypeArg,
    entity_id: IdArg,
    limit: Annotated[
        int | None, Field(ge=1, description="Max events (omitted: the configured cap).")
    ] = None,
    selected: Annotated[
        str | None,
        Field(description="Event id to build the list around, instead of from the start."),
    ] = None,
    new_events_on_top: Annotated[bool | None, Field(description="Newest events first.")] = None,
    direction: Annotated[
        str | None, Field(description="``forward`` (the default) or ``backward``.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[EntityEvent]:
    """An entity's event history (created/updated/commented/…), auto-paginated.

    Each event carries an author, a timestamp, a display title and the individual field changes.
    Capped at the configured item cap unless ``limit`` is given.
    """
    cap = config.http.cap(limit)
    return client.entities.events_list(
        entity_type,
        entity_id,
        limit=cap,
        selected=selected,
        new_events_on_top=new_events_on_top,
        direction=direction,
    )


@mcp.tool(
    name="entities_permissions_get",
    annotations={**RO, "title": "Get Tracker entity permissions"},
)
def permissions_get(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> ExtendedPermissions:
    """An entity's access settings — the READ/WRITE/GRANT ACL plus inheritance sources.

    ``acl`` lists the users, groups and roles granted each level; ``permissionSources`` names the
    parent entities this one inherits permissions from. Change them with
    ``entities_set_permissions``.
    """
    return client.entities.permissions_get(entity_type, entity_id)


@mcp.tool(
    name="entities_direct_permissions_get",
    annotations={**RO, "title": "Get Tracker entity direct permissions"},
)
def direct_permissions_get(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> Acl:
    """An entity's direct READ / WRITE / GRANT rights — the users, groups and roles holding each.

    Unlike ``entities_permissions_get`` this leaves out inheritance (``permissionSources``).
    Change the rights with ``entities_set_direct_permissions``.
    """
    return client.entities.direct_permissions_get(entity_type, entity_id)


@mcp.tool(
    name="entities_comments_list",
    annotations={**RO, "title": "List Tracker entity comments"},
)
def comments_list(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> ItemList[Comment]:
    """All comments on an entity — author, text, timestamps and summoned users."""
    return client.entities.comments_list(entity_type, entity_id)


@mcp.tool(
    name="entities_comments_get",
    annotations={**RO, "title": "Get Tracker entity comment"},
)
def comments_get(
    entity_type: TypeArg,
    entity_id: IdArg,
    comment_id: Annotated[str, Field(description="Comment id (numeric id or longId).")],
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """A single comment on an entity by id."""
    return client.entities.comments_get(entity_type, entity_id, comment_id)


@mcp.tool(name="entities_links_list", annotations={**RO, "title": "List Tracker entity links"})
def links_list(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> ItemList[Link]:
    """An entity's links to other entities — the link type and the linked entity's summary + id."""
    return client.entities.links_list(entity_type, entity_id)


@mcp.tool(
    name="entities_attachments_list",
    annotations={**RO, "title": "List Tracker entity attachments"},
)
def attachments_list(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> ItemList[Attachment]:
    """Files attached to an entity — name, size, MIME type, uploader and download URL.

    Returns metadata only. Downloading the raw bytes is CLI/SDK-only — run
    ``ycli tracker entities attachments download <FILE_ID> <FILENAME>`` — because binary blobs
    are not an MCP payload.
    """
    return client.entities.attachments_list(entity_type, entity_id)


@mcp.tool(
    name="entities_attachments_get",
    annotations={**RO, "title": "Get Tracker entity attachment"},
)
def attachments_get(
    entity_type: TypeArg,
    entity_id: IdArg,
    file_id: Annotated[str, Field(description="Attachment file id.")],
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """One attachment's metadata (name, size, MIME type, download URL).

    Downloading the raw bytes is CLI/SDK-only (``tracker entities attachments download``).
    """
    return client.entities.attachments_get(entity_type, entity_id, file_id)


@mcp.tool(
    name="entities_bulk_status_get",
    annotations={**RO, "title": "Get Tracker entity bulk-change status"},
)
def bulk_status_get(
    operation_id: Annotated[
        str, Field(description="Operation id returned by entities_bulk_update.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> BulkChangeOperation:
    """Current status of an async entity bulk-change operation started by ``entities_bulk_update``.

    ``status`` runs ``CREATED`` → ``COMPLETE`` / ``FAILED``; poll until it settles.
    """
    return client.entities.bulk_status_get(operation_id)


@mcp.tool(
    name="entities_comments_relative_list",
    annotations={**RO, "title": "List Tracker entity comments (relative)"},
)
def comments_relative_list(
    entity_type: TypeArg,
    entity_id: IdArg,
    limit: Annotated[
        int | None, Field(ge=1, description="Max comments (omitted: the configured cap).")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Comment]:
    """An entity's comments via the cursor-paginated ``…/comments/_relative`` endpoint.

    Prefer this over ``entities_comments_list`` when the comment thread is long — it drains
    pages up to ``limit`` (the configured item cap by default).
    """
    cap = config.http.cap(limit)
    return client.entities.comments_relative_list(entity_type, entity_id, limit=cap)


@mcp.tool(name="entities_create", annotations={**WRITE, "title": "Create Tracker entity"})
def create(
    entity_type: TypeArg,
    body: EntityCreate,
    fields: ReplyFields = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Create a Tracker entity (project, portfolio or goal); returns it with its id."""
    return client.entities.create(entity_type, body, fields=fields)


@mcp.tool(
    name="entities_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity"},
)
def update(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: EntityUpdate,
    expand: Expand = None,
    fields: ReplyFields = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Edit a Tracker entity; only the ``fields`` keys present in ``body`` are changed.

    Returns the updated entity.
    """
    return client.entities.update(
        entity_type,
        entity_id,
        body,
        expand=expand,
        fields=fields,
    )


@mcp.tool(
    name="entities_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity"},
)
def delete(
    entity_type: TypeArg,
    entity_id: IdArg,
    with_board: Annotated[
        bool | None, Field(description="Also delete the project's linked board.")
    ] = None,
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete a Tracker entity (project/portfolio/goal) — irreversible.

    Pass ``with_board=true`` to also delete a project's linked agile board. Returns an
    acknowledgement on success.
    """
    client.entities.delete(entity_type, entity_id, with_board=with_board)
    return Ack.deleted(entity_type, entity_id)


@mcp.tool(
    name="entities_set_permissions",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Tracker entity permissions"},
)
def set_permissions(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: PermissionsUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> ExtendedPermissions:
    """Change an entity's access rules; returns the resulting permission set.

    The ``acl`` object of ``body`` accepts only ``grant`` / ``revoke``
    actions, each mapping an access level (``READ``/``WRITE``/``GRANT``) to users/groups/roles,
    e.g. ``{"acl": {"grant": {"READ": {"users": ["8000000000000002"]}}}}``. Read the current
    ACL first with ``entities_permissions_get``.
    """
    return client.entities.set_permissions(entity_type, entity_id, body)


@mcp.tool(
    name="entities_set_direct_permissions",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Tracker entity direct permissions"},
)
def set_direct_permissions(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: DirectPermissionsUpdate,
    client: TrackerClient = Depends(tracker_client),
) -> Acl:
    """Grant and revoke an entity's direct rights; the rest stay as they are.

    ``grant`` and ``revoke`` each map READ / WRITE / GRANT to ``users`` (logins or ids),
    ``groups`` (ids) and ``roles`` (AUTHOR, OWNER, CLIENT, FOLLOWER, MEMBER). Returns the
    resulting rights. Read them first with ``entities_direct_permissions_get``.
    """
    return client.entities.set_direct_permissions(entity_type, entity_id, body)


@mcp.tool(
    name="entities_bulk_update",
    annotations={**WRITE, "title": "Bulk-update Tracker entities"},
)
def bulk_update(
    entity_type: TypeArg, body: BulkChangeUpdate, client: TrackerClient = Depends(tracker_client)
) -> BulkChangeOperation:
    """Start an async bulk field update over many entities; returns the operation.

    Poll the returned operation id with ``entities_bulk_status_get``.
    """
    return client.entities.bulk_update(entity_type, body)


@mcp.tool(
    name="entities_create_report",
    annotations={**WRITE, "title": "Create Tracker entity report"},
)
def create_report(body: ReportCreate, client: TrackerClient = Depends(tracker_client)) -> Entity:
    """Request a report over Tracker entities (``POST /entities/report/``).

    Returns the report entity.
    """
    return client.entities.create_report(body)


@mcp.tool(
    name="entities_comments_create",
    annotations={**WRITE, "title": "Add Tracker entity comment"},
)
def comments_create(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: CommentCreate,
    expand: Expand = None,
    is_add_to_followers: AddToFollowers = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Add a comment to a Tracker entity; returns the created comment."""
    return client.entities.comments_create(
        entity_type,
        entity_id,
        body,
        expand=expand,
        is_add_to_followers=is_add_to_followers,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_comments_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity comment"},
)
def comments_update(
    entity_type: TypeArg,
    entity_id: IdArg,
    comment_id: Annotated[str, Field(description="Comment id (from entities_comments_list).")],
    body: CommentUpdate,
    expand: Expand = None,
    is_add_to_followers: AddToFollowers = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Edit a comment on a Tracker entity; returns the updated comment.

    ``comment_id`` addresses the comment (get it from ``entities_comments_list``).
    """
    return client.entities.comments_update(
        entity_type,
        entity_id,
        comment_id,
        body,
        expand=expand,
        is_add_to_followers=is_add_to_followers,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity comment"},
)
def comments_delete(
    entity_type: TypeArg,
    entity_id: IdArg,
    comment_id: Annotated[str, Field(description="Comment id (from entities_comments_list).")],
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete one comment from a Tracker entity (irreversible).

    Returns an acknowledgement on success.
    """
    client.entities.comments_delete(
        entity_type, entity_id, comment_id, notify=notify, notify_author=notify_author
    )
    return Ack.deleted("comment", comment_id, on=f"{entity_type} {entity_id}")


@mcp.tool(
    name="entities_checklists_create",
    annotations={**WRITE, "title": "Add Tracker entity checklist items"},
)
def checklists_create(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: ChecklistItems,
    expand: Expand = None,
    fields: ReplyFields = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Add checklist item(s) to a Tracker entity; returns the entity with its checklist.

    ``body`` is a bare array of items, e.g. ``[{"text": "…"}]``.
    """
    return client.entities.checklists_create(
        entity_type,
        entity_id,
        body,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_checklists_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity checklist"},
)
def checklists_update(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: ChecklistItems,
    expand: Expand = None,
    fields: ReplyFields = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Replace/update a Tracker entity's checklist items in one call.

    ``body`` is a bare array of items, each with ``id``/``text``/``checked``. To edit a single
    item by id use ``entities_checklists_update_item``. Returns the entity with its checklist.
    """
    return client.entities.checklists_update(
        entity_type,
        entity_id,
        body,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_checklists_update_item",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity checklist item"},
)
def checklists_update_item(
    entity_type: TypeArg,
    entity_id: IdArg,
    item_id: Annotated[str, Field(description="Checklist item id.")],
    body: ChecklistItemInput,
    expand: Expand = None,
    fields: ReplyFields = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Edit one checklist item on a Tracker entity (text, checked state, assignee, deadline).

    Returns the entity with its updated checklist.
    """
    return client.entities.checklists_update_item(
        entity_type,
        entity_id,
        item_id,
        body,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_checklists_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity checklist"},
)
def checklists_delete(
    entity_type: TypeArg,
    entity_id: IdArg,
    expand: Expand = None,
    fields: ReplyFields = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Permanently delete the ENTIRE checklist of a Tracker entity (all items, irreversible).

    To remove a single item use ``entities_checklists_delete_item``. Returns the entity.
    """
    return client.entities.checklists_delete(
        entity_type,
        entity_id,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_checklists_delete_item",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity checklist item"},
)
def checklists_delete_item(
    entity_type: TypeArg,
    entity_id: IdArg,
    item_id: Annotated[str, Field(description="Checklist item id.")],
    expand: Expand = None,
    fields: ReplyFields = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Permanently remove one item from a Tracker entity's checklist (irreversible).

    Returns the entity with its remaining checklist.
    """
    return client.entities.checklists_delete_item(
        entity_type,
        entity_id,
        item_id,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_checklists_move",
    annotations={**WRITE, "title": "Move Tracker entity checklist item"},
)
def checklists_move(
    entity_type: TypeArg,
    entity_id: IdArg,
    item_id: Annotated[str, Field(description="Checklist item id to move.")],
    body: ChecklistMove,
    expand: Expand = None,
    fields: ReplyFields = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Reorder a checklist item within a Tracker entity's checklist.

    Returns the entity with its reordered checklist.
    """
    return client.entities.checklists_move(
        entity_type,
        entity_id,
        item_id,
        body,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_links_create",
    annotations={**WRITE, "title": "Link Tracker entities"},
)
def links_create(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: LinkInput,
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Link a Tracker entity to another entity (e.g. ``relates``, ``depends on``).

    Returns an acknowledgement on success.
    """
    client.entities.links_create(entity_type, entity_id, body)
    return Ack.linked(entity_type, entity_id, body.entity, body.relationship)


@mcp.tool(
    name="entities_links_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity link"},
)
def links_delete(
    entity_type: TypeArg,
    entity_id: IdArg,
    right: Annotated[str, Field(description="Id of the linked entity to unlink.")],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Remove the link between a Tracker entity and another entity (irreversible).

    ``right`` is the id of the entity on the other end (see ``entities_links_list``). Returns
    an acknowledgement on success.
    """
    client.entities.links_delete(entity_type, entity_id, right)
    return Ack.unlinked(entity_type, entity_id, right)


@mcp.tool(
    name="entities_attachments_attach",
    annotations={**WRITE, "title": "Attach Tracker entity file"},
)
def attachments_attach(
    entity_type: TypeArg,
    entity_id: IdArg,
    temp_file_id: Annotated[
        str, Field(description="Temporary file id from a prior POST /attachments upload.")
    ],
    expand: Expand = None,
    fields: ReplyFields = None,
    notify: Notify = None,
    notify_author: NotifyAuthor = None,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Attach a previously uploaded temporary file to a Tracker entity.

    Requires a ``temp_file_id`` from the Tracker temporary-upload endpoint (not wrapped by
    ycli — files are usually seeded via the UI). Returns the entity.
    """
    return client.entities.attachments_attach(
        entity_type,
        entity_id,
        temp_file_id,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@mcp.tool(
    name="entities_attachments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity attachment"},
)
def attachments_delete(
    entity_type: TypeArg,
    entity_id: IdArg,
    file_id: Annotated[
        str, Field(description="Attachment file id (from entities_attachments_list).")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete an attachment from a Tracker entity (irreversible).

    The API answers with an empty body; returns an acknowledgement on success.
    """
    client.entities.attachments_delete(entity_type, entity_id, file_id)
    return Ack.deleted("attachment", file_id, on=f"{entity_type} {entity_id}")
