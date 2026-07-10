"""Tracker Entities FastMCP tools — read-only (projects / portfolios / goals).

Exposes the reads only: fetch/search an entity, its comments, links and attachment metadata,
and its event history. Every write (create/edit/delete, checklist & link CRUD, bulk change) is
CLI/SDK-only (ARCH-3); the binary attachment download is CLI/SDK-only too (a base64 blob is not
a useful MCP payload) — its ``…_list`` / ``…_get`` metadata siblings are the MCP entry points.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import RO, TAGS, app_config, tracker_client
from ycli.yandex.tracker.entities.models import (
    Attachment,
    AttachmentList,
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
    cfg: AppConfig = Depends(app_config),
) -> EntityEventList:
    """An entity's event history (created/updated/commented/…), auto-paginated.

    Each event carries an author, a timestamp, a display title and the individual field changes.
    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given.

    Example:
        >>> entities_events_list("project", "655f", limit=50)  # doctest: +SKIP
    """
    return client.entities.history(entity_type, entity_id, limit=limit or cfg.max_items)


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
    parent entities this one inherits permissions from. Setting permissions is CLI/SDK-only
    (``tracker entities set-permissions``).

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
