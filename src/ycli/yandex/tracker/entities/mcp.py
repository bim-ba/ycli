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
from ycli.yandex.models import Ack
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
from ycli.yandex.tracker.entities.models import (
    Attachment,
    AttachmentList,
    BulkChangeOperation,
    Comment,
    CommentList,
    Entity,
    EntityEventList,
    EntityList,
    ExtendedPermissions,
    LinkList,
)

mcp = FastMCP("tracker-entities")

TypeArg = Annotated[str, Field(description="Entity type: ``project``, ``portfolio`` or ``goal``.")]
IdArg = Annotated[str, Field(description="Entity id (or shortId).")]


@mcp.tool(name="entities_get", annotations={**RO, "title": "Get Tracker entity"}, tags=TAGS)
def get(
    entity_type: TypeArg,
    entity_id: IdArg,
    fields: Annotated[
        str,
        Field(description="Comma-separated extra fields, e.g. ``keyResultItems,checklistItems``."),
    ] = "",
    expand: Annotated[str, Field(description="Extra info, e.g. ``attachments``.")] = "",
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """A single Tracker entity (project, portfolio or goal) by id, with its ``fields`` block.

    Pass ``fields`` to pull extra parameters into the response — ``keyResultItems`` for a goal's
    key results, ``checklistItems`` for a project/portfolio checklist, ``metricItems`` for its
    metric widgets, or ``summary,description,entityStatus`` for the basics. Use
    ``entities_search`` to discover ids first.

    Example:
        >>> entities_get("project", "655f", fields="summary,entityStatus")  # doctest: +SKIP
    """
    return client.entities.get(entity_type, entity_id, expand=expand or None, fields=fields or None)


@mcp.tool(name="entities_search", annotations={**RO, "title": "Search Tracker entities"}, tags=TAGS)
def search(
    entity_type: TypeArg,
    input_text: Annotated[str, Field(description="Substring to match in the entity name.")] = "",
    order_by: Annotated[str, Field(description="Field key to sort the results by.")] = "",
    fields: Annotated[str, Field(description="Comma-separated extra fields to include.")] = "",
    client: TrackerClient = Depends(tracker_client),
) -> EntityList:
    """Entities of a given type matching a name substring, sorted server-side.

    Returns a flat list of entities. Pass ``input_text`` to match part of the name and
    ``order_by`` (e.g. ``entityStatus``) to sort. For richer filtering (by author, status,
    followers, …) use the CLI ``tracker entities search --filter`` which accepts an arbitrary
    filter object.

    Example:
        >>> entities_search("goal", input_text="Q4", order_by="entityStatus")  # doctest: +SKIP
    """
    body: dict[str, str] = {}
    if input_text:
        body["input"] = input_text
    if order_by:
        body["orderBy"] = order_by
    return client.entities.search(entity_type, body, fields=fields or None)


@mcp.tool(
    name="entities_events_list",
    annotations={**RO, "title": "List Tracker entity history"},
    tags=TAGS,
)
def events_list(
    entity_type: TypeArg,
    entity_id: IdArg,
    limit: Annotated[int, Field(description="Max events (0 = YCLI_MAX_ITEMS cap).")] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> EntityEventList:
    """An entity's event history (created/updated/commented/…), auto-paginated.

    Each event carries an author, a timestamp, a display title and the individual field changes.
    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given.

    Example:
        >>> entities_events_list("project", "655f", limit=50)  # doctest: +SKIP
    """
    cap = resolve_cap(limit, config.max_items)
    return client.entities.history(entity_type, entity_id, limit=cap)


@mcp.tool(
    name="entities_permissions_get",
    annotations={**RO, "title": "Get Tracker entity permissions"},
    tags=TAGS,
)
def permissions_get(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> ExtendedPermissions:
    """An entity's access settings — the READ/WRITE/GRANT ACL plus inheritance sources.

    ``acl`` lists the users, groups and roles granted each level; ``permissionSources`` names the
    parent entities this one inherits permissions from. Change them with
    ``entities_set_permissions``.

    Example:
        >>> entities_permissions_get("project", "655f")  # doctest: +SKIP
    """
    return client.entities.permissions(entity_type, entity_id)


@mcp.tool(
    name="entities_comments_list",
    annotations={**RO, "title": "List Tracker entity comments"},
    tags=TAGS,
)
def comments_list(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> CommentList:
    """All comments on an entity — author, text, timestamps and summoned users.

    Example:
        >>> entities_comments_list("project", "655f")  # doctest: +SKIP
    """
    return client.entities.comments_list(entity_type, entity_id)


@mcp.tool(
    name="entities_comments_get",
    annotations={**RO, "title": "Get Tracker entity comment"},
    tags=TAGS,
)
def comments_get(
    entity_type: TypeArg,
    entity_id: IdArg,
    comment_id: Annotated[str, Field(description="Comment id (numeric id or longId).")],
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """A single comment on an entity by id.

    Example:
        >>> entities_comments_get("project", "655f", "22")  # doctest: +SKIP
    """
    return client.entities.comments_get(entity_type, entity_id, comment_id)


@mcp.tool(
    name="entities_links_list", annotations={**RO, "title": "List Tracker entity links"}, tags=TAGS
)
def links_list(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> LinkList:
    """An entity's links to other entities — the link type and the linked entity's summary + id.

    Example:
        >>> entities_links_list("project", "655f")  # doctest: +SKIP
    """
    return client.entities.links_list(entity_type, entity_id)


@mcp.tool(
    name="entities_attachments_list",
    annotations={**RO, "title": "List Tracker entity attachments"},
    tags=TAGS,
)
def attachments_list(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> AttachmentList:
    """Files attached to an entity — name, size, MIME type, uploader and download URL.

    Returns metadata only. Downloading the raw bytes is CLI/SDK-only — run
    ``ycli tracker entities attachments download <FILE_ID> <FILENAME>`` — because binary blobs
    are not an MCP payload.

    Example:
        >>> entities_attachments_list("project", "655f")  # doctest: +SKIP
    """
    return client.entities.attachments_list(entity_type, entity_id)


@mcp.tool(
    name="entities_attachments_get",
    annotations={**RO, "title": "Get Tracker entity attachment"},
    tags=TAGS,
)
def attachments_get(
    entity_type: TypeArg,
    entity_id: IdArg,
    file_id: Annotated[str, Field(description="Attachment file id.")],
    client: TrackerClient = Depends(tracker_client),
) -> Attachment:
    """One attachment's metadata (name, size, MIME type, download URL).

    Downloading the raw bytes is CLI/SDK-only (``tracker entities attachments download``).

    Example:
        >>> entities_attachments_get("project", "655f", "5")  # doctest: +SKIP
    """
    return client.entities.attachments_get(entity_type, entity_id, file_id)


@mcp.tool(
    name="entities_bulk_status_get",
    annotations={**RO, "title": "Get Tracker entity bulk-change status"},
    tags=TAGS,
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
    return client.entities.bulk_status(operation_id)


@mcp.tool(
    name="entities_comments_relative_list",
    annotations={**RO, "title": "List Tracker entity comments (relative)"},
    tags=TAGS,
)
def comments_relative_list(
    entity_type: TypeArg,
    entity_id: IdArg,
    limit: Annotated[int, Field(description="Max comments (0 = YCLI_MAX_ITEMS cap).")] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> CommentList:
    """An entity's comments via the cursor-paginated ``…/comments/_relative`` endpoint.

    Prefer this over ``entities_comments_list`` when the comment thread is long — it drains
    pages up to ``limit`` (default YCLI_MAX_ITEMS).
    """
    cap = resolve_cap(limit, config.max_items)
    return client.entities.comments_relative(entity_type, entity_id, limit=cap)


@mcp.tool(
    name="entities_create", annotations={**WRITE, "title": "Create Tracker entity"}, tags=WRITE_TAGS
)
def create(
    entity_type: TypeArg, body: dict, client: TrackerClient = Depends(tracker_client)
) -> Entity:
    """Create a Tracker entity (project, portfolio or goal); returns it with its id.

    ``body`` is the raw API payload — at minimum ``{"fields": {"summary": "…"}}``; other
    ``fields`` keys include ``description``, ``entityStatus``, ``lead``, ``teamUsers``,
    ``start``/``end``.
    """
    return client.entities.create(entity_type, body)


@mcp.tool(
    name="entities_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity"},
    tags=WRITE_TAGS,
)
def edit(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Edit a Tracker entity; only the ``fields`` keys present in ``body`` are changed.

    ``body`` is the raw API payload, e.g. ``{"fields": {"summary": "…", "entityStatus":
    "in_progress"}}``. Returns the updated entity.
    """
    return client.entities.edit(entity_type, entity_id, body)


@mcp.tool(
    name="entities_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity"},
    tags=WRITE_TAGS,
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
    return Ack(detail=f"deleted {entity_type} {entity_id}")


@mcp.tool(
    name="entities_set_permissions",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Tracker entity permissions"},
    tags=WRITE_TAGS,
)
def set_permissions(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> ExtendedPermissions:
    """Change an entity's access rules; returns the resulting permission set.

    ``body`` is the raw API payload; its ``acl`` object accepts only ``grant`` / ``revoke``
    actions, each mapping an access level (``READ``/``WRITE``/``GRANT``) to users/groups/roles,
    e.g. ``{"acl": {"grant": {"READ": {"users": ["8000000000000002"]}}}}``. Read the current
    ACL first with ``entities_permissions_get``.
    """
    return client.entities.set_permissions(entity_type, entity_id, body)


@mcp.tool(
    name="entities_bulk_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Bulk-update Tracker entities"},
    tags=WRITE_TAGS,
)
def bulk_update(
    entity_type: TypeArg, body: dict, client: TrackerClient = Depends(tracker_client)
) -> BulkChangeOperation:
    """Start an async bulk field update over many entities; returns the operation.

    ``body`` is the raw API payload: ``{"entityIds": […], "values": {…}}``. Poll the returned
    operation id with ``entities_bulk_status_get``.
    """
    return client.entities.bulk_update(entity_type, body)


@mcp.tool(
    name="entities_create_report",
    annotations={**WRITE, "title": "Create Tracker entity report"},
    tags=WRITE_TAGS,
)
def create_report(body: dict, client: TrackerClient = Depends(tracker_client)) -> Entity:
    """Request a report over Tracker entities (``POST /entities/report/``).

    ``body`` is the raw API payload describing the report scope and grouping. Returns the
    report entity.
    """
    return client.entities.create_report(body)


@mcp.tool(
    name="entities_comments_create",
    annotations={**WRITE, "title": "Add Tracker entity comment"},
    tags=WRITE_TAGS,
)
def comments_create(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Add a comment to a Tracker entity; returns the created comment.

    ``body`` is the raw API payload — at minimum ``{"text": "…"}`` (YFM markup allowed).
    """
    return client.entities.comments_create(entity_type, entity_id, body)


@mcp.tool(
    name="entities_comments_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity comment"},
    tags=WRITE_TAGS,
)
def comments_edit(
    entity_type: TypeArg,
    entity_id: IdArg,
    comment_id: Annotated[str, Field(description="Comment id (from entities_comments_list).")],
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Comment:
    """Edit a comment on a Tracker entity; returns the updated comment.

    ``comment_id`` addresses the comment (get it from ``entities_comments_list``); ``body`` is
    the raw API payload with the new content, e.g. ``{"text": "…"}``.
    """
    return client.entities.comments_edit(entity_type, entity_id, comment_id, body)


@mcp.tool(
    name="entities_comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity comment"},
    tags=WRITE_TAGS,
)
def comments_delete(
    entity_type: TypeArg,
    entity_id: IdArg,
    comment_id: Annotated[str, Field(description="Comment id (from entities_comments_list).")],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Permanently delete one comment from a Tracker entity (irreversible).

    Returns an acknowledgement on success.
    """
    client.entities.comments_delete(entity_type, entity_id, comment_id)
    return Ack(detail=f"deleted comment {comment_id} on {entity_type} {entity_id}")


@mcp.tool(
    name="entities_checklists_create",
    annotations={**WRITE, "title": "Add Tracker entity checklist items"},
    tags=WRITE_TAGS,
)
def checklists_create(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Add checklist item(s) to a Tracker entity; returns the entity with its checklist.

    ``body`` is the raw API payload — a single item ``{"text": "…"}`` or a batch
    ``{"notify": …, "items": [{"text": "…"}, …]}``.
    """
    return client.entities.checklists_create(entity_type, entity_id, body)


@mcp.tool(
    name="entities_checklists_edit",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity checklist"},
    tags=WRITE_TAGS,
)
def checklists_edit(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Replace/update a Tracker entity's checklist items in one call.

    ``body`` is the raw API payload (an array of items or ``{"items": […]}``, each with
    ``id``/``text``/``checked``). To edit a single item by id use
    ``entities_checklists_edit_item``. Returns the entity with its checklist.
    """
    return client.entities.checklists_edit(entity_type, entity_id, body)


@mcp.tool(
    name="entities_checklists_edit_item",
    annotations={**WRITE_IDEMPOTENT, "title": "Edit Tracker entity checklist item"},
    tags=WRITE_TAGS,
)
def checklists_edit_item(
    entity_type: TypeArg,
    entity_id: IdArg,
    item_id: Annotated[str, Field(description="Checklist item id.")],
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Edit one checklist item on a Tracker entity (text, checked state, assignee, deadline).

    ``body`` carries the fields to change, e.g. ``{"text": "…", "checked": true}``. Returns
    the entity with its updated checklist.
    """
    return client.entities.checklists_edit_item(entity_type, entity_id, item_id, body)


@mcp.tool(
    name="entities_checklists_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity checklist"},
    tags=WRITE_TAGS,
)
def checklists_delete(
    entity_type: TypeArg, entity_id: IdArg, client: TrackerClient = Depends(tracker_client)
) -> Entity:
    """Permanently delete the ENTIRE checklist of a Tracker entity (all items, irreversible).

    To remove a single item use ``entities_checklists_delete_item``. Returns the entity.
    """
    return client.entities.checklists_delete(entity_type, entity_id)


@mcp.tool(
    name="entities_checklists_delete_item",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity checklist item"},
    tags=WRITE_TAGS,
)
def checklists_delete_item(
    entity_type: TypeArg,
    entity_id: IdArg,
    item_id: Annotated[str, Field(description="Checklist item id.")],
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Permanently remove one item from a Tracker entity's checklist (irreversible).

    Returns the entity with its remaining checklist.
    """
    return client.entities.checklists_delete_item(entity_type, entity_id, item_id)


@mcp.tool(
    name="entities_checklists_move",
    annotations={**WRITE, "title": "Move Tracker entity checklist item"},
    tags=WRITE_TAGS,
)
def checklists_move(
    entity_type: TypeArg,
    entity_id: IdArg,
    item_id: Annotated[str, Field(description="Checklist item id to move.")],
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Reorder a checklist item within a Tracker entity's checklist.

    ``body`` is the raw API payload, e.g. ``{"before": "<other item id>"}``. Returns the
    entity with its reordered checklist.
    """
    return client.entities.checklists_move(entity_type, entity_id, item_id, body)


@mcp.tool(
    name="entities_links_create",
    annotations={**WRITE, "title": "Link Tracker entities"},
    tags=WRITE_TAGS,
)
def links_create(
    entity_type: TypeArg,
    entity_id: IdArg,
    body: dict,
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Link a Tracker entity to another entity.

    ``body`` is the raw API payload ``{"relationship": "…", "entity": "<other entity id>"}``
    (e.g. ``relates``, ``depends on``). Returns an acknowledgement on success.
    """
    client.entities.links_create(entity_type, entity_id, body)
    return Ack(detail=f"linked {entity_type} {entity_id}")


@mcp.tool(
    name="entities_links_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity link"},
    tags=WRITE_TAGS,
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
    return Ack(detail=f"deleted link to {right} on {entity_type} {entity_id}")


@mcp.tool(
    name="entities_attachments_attach",
    annotations={**WRITE, "title": "Attach Tracker entity file"},
    tags=WRITE_TAGS,
)
def attachments_attach(
    entity_type: TypeArg,
    entity_id: IdArg,
    temp_file_id: Annotated[
        str, Field(description="Temporary file id from a prior POST /attachments upload.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Entity:
    """Attach a previously uploaded temporary file to a Tracker entity.

    Requires a ``temp_file_id`` from the Tracker temporary-upload endpoint (not wrapped by
    ycli — files are usually seeded via the UI). Returns the entity.
    """
    return client.entities.attachments_attach(entity_type, entity_id, temp_file_id)


@mcp.tool(
    name="entities_attachments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker entity attachment"},
    tags=WRITE_TAGS,
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
    return Ack(detail=f"deleted attachment {file_id} on {entity_type} {entity_id}")
