"""Tracker ``/entities`` operations (projects, portfolios, goals), each declared once (sans-IO).

``entity_type`` (project | portfolio | goal) is the first path segment of every entity route.

Examples:
    >>> get("project", "655f", expand=None, fields="summary").params
    {'expand': None, 'fields': 'summary'}
    >>> search("goal", {}, fields=None, per_page=None, page=None).effect
    'read'
    >>> events = events_list(
    ...     "project", "655f", per_page=100, selected=None, new_events_on_top=None, direction=None
    ... )
    >>> events.endpoint.path
    'entities/project/655f/events/_relative'
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.entities.models import (
    ACL,
    Attachment,
    BulkChangeOperation,
    BulkChangeUpdate,
    ChecklistItemInput,
    ChecklistMove,
    Comment,
    CommentsRelativeResponse,
    CommentUpdate,
    DirectPermissionsUpdate,
    Entity,
    EntityCreate,
    EntityEvent,
    EntityEventsResponse,
    EntitySearch,
    EntitySearchResponse,
    EntityUpdate,
    ExtendedPermissions,
    Link,
    LinkInput,
    PermissionsUpdate,
    ReportCreate,
)

if TYPE_CHECKING:
    from ycli.yandex.tracker.models import CommentCreate

# The most events / comments one ``_relative`` page returns; a smaller cap asks for fewer.
RELATIVE_PAGE_SIZE = 100


def _entity(entity_type: str, entity_id: str) -> str:
    return f"entities/{segment(entity_type)}/{segment(entity_id)}"


# ---- core ----------------------------------------------------------------------------------


def create(
    entity_type: str,
    body: EntityCreate,
    *,
    fields: str | None,
) -> Endpoint[Entity]:
    return Endpoint(
        "POST", f"entities/{segment(entity_type)}", Entity, json=body, params={"fields": fields}
    )


def get(
    entity_type: str, entity_id: str, *, expand: str | None, fields: str | None
) -> Endpoint[Entity]:
    params = {"expand": expand, "fields": fields}
    return Endpoint("GET", _entity(entity_type, entity_id), Entity, params=params)


def update(
    entity_type: str,
    entity_id: str,
    body: EntityUpdate,
    *,
    expand: str | None,
    fields: str | None,
) -> Endpoint[Entity]:
    return Endpoint(
        "PATCH",
        _entity(entity_type, entity_id),
        Entity,
        json=body,
        params={"expand": expand, "fields": fields},
    )


def delete(entity_type: str, entity_id: str, *, with_board: bool | None) -> Endpoint[None]:
    params = {"withBoard": with_board}
    return Endpoint("DELETE", _entity(entity_type, entity_id), params=params)


def search(
    entity_type: str,
    body: EntitySearch,
    *,
    fields: str | None,
    per_page: int | None,
    page: int | None,
) -> Endpoint[EntitySearchResponse]:
    """``POST …/_search`` only reads; one page, the one ``per_page``/``page`` select."""
    return Endpoint(
        "POST",
        f"entities/{segment(entity_type)}/_search",
        EntitySearchResponse,
        params={"fields": fields, "perPage": per_page, "page": page},
        json=body,
        effect="read",
    )


def events_list(
    entity_type: str,
    entity_id: str,
    *,
    per_page: int,
    selected: str | None,
    new_events_on_top: bool | None,
    direction: str | None,
) -> Paged[EntityEventsResponse, EntityEvent]:
    """``GET …/events/_relative``, each next page from the last event's id (``from=``)."""
    return Paged(
        Endpoint(
            "GET",
            f"{_entity(entity_type, entity_id)}/events/_relative",
            EntityEventsResponse,
            params={
                "perPage": per_page,
                "selected": selected,
                "newEventsOnTop": new_events_on_top,
                "direction": direction,
            },
        ),
        RelativeIDPagination(id_of=lambda event: event.id, id_param="from"),
        lambda page: page.events,
    )


def permissions_get(entity_type: str, entity_id: str) -> Endpoint[ExtendedPermissions]:
    path = f"{_entity(entity_type, entity_id)}/extendedPermissions"
    return Endpoint("GET", path, ExtendedPermissions)


def permissions_update(
    entity_type: str, entity_id: str, body: PermissionsUpdate
) -> Endpoint[ExtendedPermissions]:
    path = f"{_entity(entity_type, entity_id)}/extendedPermissions"
    return Endpoint("PATCH", path, ExtendedPermissions, json=body)


def permissions_get_direct(entity_type: str, entity_id: str) -> Endpoint[ACL]:
    return Endpoint("GET", f"{_entity(entity_type, entity_id)}/permissions", ACL)


def permissions_update_direct(
    entity_type: str, entity_id: str, body: DirectPermissionsUpdate
) -> Endpoint[ACL]:
    return Endpoint("PATCH", f"{_entity(entity_type, entity_id)}/permissions", ACL, json=body)


def update_bulk(entity_type: str, body: BulkChangeUpdate) -> Endpoint[BulkChangeOperation]:
    """Each call starts a new async operation: a plain, non-idempotent write."""
    path = f"entities/{segment(entity_type)}/bulkchange/_update"
    return Endpoint("POST", path, BulkChangeOperation, json=body)


def bulk_get(bulk_id: str) -> Endpoint[BulkChangeOperation]:
    return Endpoint("GET", f"bulkchange/{segment(bulk_id)}", BulkChangeOperation)


def reports_create(body: ReportCreate) -> Endpoint[Entity]:
    return Endpoint("POST", "entities/report/", Entity, json=body)


# ---- comments ------------------------------------------------------------------------------


def comments_list(
    entity_type: str, entity_id: str, *, expand: str | None
) -> Endpoint[ItemList[Comment]]:
    path = f"{_entity(entity_type, entity_id)}/comments"
    return Endpoint("GET", path, ItemList[Comment], params={"expand": expand})


def comments_list_relative(
    entity_type: str, entity_id: str, *, per_page: int
) -> Paged[CommentsRelativeResponse, Comment]:
    """``GET …/comments/_relative``, each next page from the last comment's ``longId``."""
    return Paged(
        Endpoint(
            "GET",
            f"{_entity(entity_type, entity_id)}/comments/_relative",
            CommentsRelativeResponse,
            params={"perPage": per_page},
        ),
        RelativeIDPagination(id_of=lambda comment: comment.long_id, id_param="from"),
        lambda page: page.comments,
    )


def comments_get(
    entity_type: str, entity_id: str, comment_id: str, *, expand: str | None
) -> Endpoint[Comment]:
    path = f"{_entity(entity_type, entity_id)}/comments/{segment(comment_id)}"
    return Endpoint("GET", path, Comment, params={"expand": expand})


def comments_create(
    entity_type: str,
    entity_id: str,
    body: CommentCreate,
    *,
    expand: str | None,
    is_add_to_followers: bool | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Comment]:
    return Endpoint(
        "POST",
        f"{_entity(entity_type, entity_id)}/comments",
        Comment,
        json=body,
        params={
            "expand": expand,
            "isAddToFollowers": is_add_to_followers,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def comments_update(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    body: CommentUpdate,
    *,
    expand: str | None,
    is_add_to_followers: bool | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Comment]:
    path = f"{_entity(entity_type, entity_id)}/comments/{segment(comment_id)}"
    return Endpoint(
        "PATCH",
        path,
        Comment,
        json=body,
        params={
            "expand": expand,
            "isAddToFollowers": is_add_to_followers,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def comments_delete(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    *,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[None]:
    path = f"{_entity(entity_type, entity_id)}/comments/{segment(comment_id)}"
    return Endpoint("DELETE", path, params={"notify": notify, "notifyAuthor": notify_author})


# ---- checklists ----------------------------------------------------------------------------


def checklists_create(
    entity_type: str,
    entity_id: str,
    body: ItemList[ChecklistItemInput],
    *,
    expand: str | None,
    fields: str | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Entity]:
    path = f"{_entity(entity_type, entity_id)}/checklistItems"
    return Endpoint(
        "POST",
        path,
        Entity,
        json=body,
        params={
            "expand": expand,
            "fields": fields,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def checklists_update(
    entity_type: str,
    entity_id: str,
    body: ItemList[ChecklistItemInput],
    *,
    expand: str | None,
    fields: str | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Entity]:
    path = f"{_entity(entity_type, entity_id)}/checklistItems"
    return Endpoint(
        "PATCH",
        path,
        Entity,
        json=body,
        params={
            "expand": expand,
            "fields": fields,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def checklists_items_update(
    entity_type: str,
    entity_id: str,
    item_id: str,
    body: ChecklistItemInput,
    *,
    expand: str | None,
    fields: str | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Entity]:
    path = f"{_entity(entity_type, entity_id)}/checklistItems/{segment(item_id)}"
    return Endpoint(
        "PATCH",
        path,
        Entity,
        json=body,
        params={
            "expand": expand,
            "fields": fields,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def checklists_delete(
    entity_type: str,
    entity_id: str,
    *,
    expand: str | None,
    fields: str | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Entity]:
    return Endpoint(
        "DELETE",
        f"{_entity(entity_type, entity_id)}/checklistItems",
        Entity,
        params={
            "expand": expand,
            "fields": fields,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def checklists_items_delete(
    entity_type: str,
    entity_id: str,
    item_id: str,
    *,
    expand: str | None,
    fields: str | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Entity]:
    path = f"{_entity(entity_type, entity_id)}/checklistItems/{segment(item_id)}"
    return Endpoint(
        "DELETE",
        path,
        Entity,
        params={
            "expand": expand,
            "fields": fields,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def checklists_move(
    entity_type: str,
    entity_id: str,
    item_id: str,
    body: ChecklistMove,
    *,
    expand: str | None,
    fields: str | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Entity]:
    path = f"{_entity(entity_type, entity_id)}/checklistItems/{segment(item_id)}/_move"
    return Endpoint(
        "POST",
        path,
        Entity,
        json=body,
        params={
            "expand": expand,
            "fields": fields,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


# ---- links ---------------------------------------------------------------------------------


def links_list(entity_type: str, entity_id: str, *, fields: str | None) -> Endpoint[ItemList[Link]]:
    path = f"{_entity(entity_type, entity_id)}/links"
    return Endpoint("GET", path, ItemList[Link], params={"fields": fields})


def links_create(entity_type: str, entity_id: str, body: LinkInput) -> Endpoint[None]:
    """``POST …/links`` answers 200 with no body."""
    return Endpoint("POST", f"{_entity(entity_type, entity_id)}/links", json=body)


def links_delete(entity_type: str, entity_id: str, right: str) -> Endpoint[None]:
    path = f"{_entity(entity_type, entity_id)}/links"
    return Endpoint("DELETE", path, params={"right": right})


# ---- attachments ---------------------------------------------------------------------------


def attachments_list(entity_type: str, entity_id: str) -> Endpoint[ItemList[Attachment]]:
    return Endpoint("GET", f"{_entity(entity_type, entity_id)}/attachments", ItemList[Attachment])


def attachments_get(entity_type: str, entity_id: str, file_id: str) -> Endpoint[Attachment]:
    path = f"{_entity(entity_type, entity_id)}/attachments/{segment(file_id)}"
    return Endpoint("GET", path, Attachment)


def attachments_download(file_id: str, filename: str) -> Endpoint[bytes]:
    return Endpoint("GET", f"attachments/{segment(file_id)}/{segment(filename)}", bytes)


def attachments_attach(
    entity_type: str,
    entity_id: str,
    temp_file_id: str,
    *,
    expand: str | None,
    fields: str | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Entity]:
    path = f"{_entity(entity_type, entity_id)}/attachments/{segment(temp_file_id)}"
    return Endpoint(
        "POST",
        path,
        Entity,
        params={
            "expand": expand,
            "fields": fields,
            "notify": notify,
            "notifyAuthor": notify_author,
        },
    )


def attachments_delete(entity_type: str, entity_id: str, file_id: str) -> Endpoint[None]:
    """``DELETE …/attachments/{file_id}`` answers with an empty body."""
    path = f"{_entity(entity_type, entity_id)}/attachments/{segment(file_id)}"
    return Endpoint("DELETE", path)
