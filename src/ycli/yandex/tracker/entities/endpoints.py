"""Tracker ``/entities`` operations (projects, portfolios, goals), each declared once (sans-IO).

``entity_type`` (project | portfolio | goal) is the first path segment of every entity route.

Examples:
    >>> get_entity("project", "655f", expand=None, fields="summary").params
    {'expand': None, 'fields': 'summary'}
    >>> search_entities("goal", {}, fields=None, per_page=None, page=None).effect
    'read'
    >>> events = list_events(
    ...     "project", "655f", per_page=100, selected=None, new_events_on_top=None, direction=None
    ... )
    >>> events.endpoint.path
    'entities/project/655f/events/_relative'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIdPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.entities.models import (
    Acl,
    Attachment,
    BulkChangeOperation,
    Comment,
    CommentsRelativeResponse,
    Entity,
    EntityEvent,
    EntityEventsResponse,
    EntitySearchResponse,
    ExtendedPermissions,
    Link,
)

# The most events / comments one ``_relative`` page returns; a smaller cap asks for fewer.
RELATIVE_PAGE_SIZE = 100


def _entity(entity_type: str, entity_id: str) -> str:
    return f"entities/{segment(entity_type)}/{segment(entity_id)}"


# ---- core ----------------------------------------------------------------------------------


def create_entity(
    entity_type: str,
    body: dict[str, Any],
    *,
    fields: str | None,
) -> Endpoint[Entity]:
    return Endpoint(
        "POST", f"entities/{segment(entity_type)}", Entity, json=body, params={"fields": fields}
    )


def get_entity(
    entity_type: str, entity_id: str, *, expand: str | None, fields: str | None
) -> Endpoint[Entity]:
    params = {"expand": expand, "fields": fields}
    return Endpoint("GET", _entity(entity_type, entity_id), Entity, params=params)


def edit_entity(
    entity_type: str,
    entity_id: str,
    body: dict[str, Any],
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


def delete_entity(entity_type: str, entity_id: str, *, with_board: bool | None) -> Endpoint[None]:
    params = {"withBoard": with_board}
    return Endpoint("DELETE", _entity(entity_type, entity_id), params=params)


def search_entities(
    entity_type: str,
    body: dict[str, Any],
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


def list_events(
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
        RelativeIdPagination(id_of=lambda event: event.id, id_param="from"),
        lambda page: page.events,
    )


def get_permissions(entity_type: str, entity_id: str) -> Endpoint[ExtendedPermissions]:
    path = f"{_entity(entity_type, entity_id)}/extendedPermissions"
    return Endpoint("GET", path, ExtendedPermissions)


def set_permissions(
    entity_type: str, entity_id: str, body: dict[str, Any]
) -> Endpoint[ExtendedPermissions]:
    path = f"{_entity(entity_type, entity_id)}/extendedPermissions"
    return Endpoint("PATCH", path, ExtendedPermissions, json=body)


def get_direct_permissions(entity_type: str, entity_id: str) -> Endpoint[Acl]:
    return Endpoint("GET", f"{_entity(entity_type, entity_id)}/permissions", Acl)


def set_direct_permissions(entity_type: str, entity_id: str, body: dict[str, Any]) -> Endpoint[Acl]:
    return Endpoint("PATCH", f"{_entity(entity_type, entity_id)}/permissions", Acl, json=body)


def bulk_update(entity_type: str, body: dict[str, Any]) -> Endpoint[BulkChangeOperation]:
    """Each call starts a new async operation: a plain, non-idempotent write."""
    path = f"entities/{segment(entity_type)}/bulkchange/_update"
    return Endpoint("POST", path, BulkChangeOperation, json=body)


def get_bulk_status(operation_id: str) -> Endpoint[BulkChangeOperation]:
    return Endpoint("GET", f"bulkchange/{segment(operation_id)}", BulkChangeOperation)


def create_report(body: dict[str, Any]) -> Endpoint[Entity]:
    return Endpoint("POST", "entities/report/", Entity, json=body)


# ---- comments ------------------------------------------------------------------------------


def list_comments(
    entity_type: str, entity_id: str, *, expand: str | None
) -> Endpoint[ItemList[Comment]]:
    path = f"{_entity(entity_type, entity_id)}/comments"
    return Endpoint("GET", path, ItemList[Comment], params={"expand": expand})


def list_comments_relative(
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
        RelativeIdPagination(id_of=lambda comment: comment.long_id, id_param="from"),
        lambda page: page.comments,
    )


def get_comment(
    entity_type: str, entity_id: str, comment_id: str, *, expand: str | None
) -> Endpoint[Comment]:
    path = f"{_entity(entity_type, entity_id)}/comments/{segment(comment_id)}"
    return Endpoint("GET", path, Comment, params={"expand": expand})


def create_comment(
    entity_type: str,
    entity_id: str,
    body: dict[str, Any],
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


def edit_comment(
    entity_type: str,
    entity_id: str,
    comment_id: str,
    body: dict[str, Any],
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


def delete_comment(
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


def create_checklist_items(
    entity_type: str,
    entity_id: str,
    body: list[dict[str, Any]],
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


def edit_checklist(
    entity_type: str,
    entity_id: str,
    body: list[dict[str, Any]],
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


def edit_checklist_item(
    entity_type: str,
    entity_id: str,
    item_id: str,
    body: dict[str, Any],
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


def delete_checklist(
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


def delete_checklist_item(
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


def move_checklist_item(
    entity_type: str,
    entity_id: str,
    item_id: str,
    body: dict[str, Any],
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


def list_links(entity_type: str, entity_id: str, *, fields: str | None) -> Endpoint[ItemList[Link]]:
    path = f"{_entity(entity_type, entity_id)}/links"
    return Endpoint("GET", path, ItemList[Link], params={"fields": fields})


def create_link(entity_type: str, entity_id: str, body: dict[str, Any]) -> Endpoint[None]:
    """``POST …/links`` answers 200 with no body."""
    return Endpoint("POST", f"{_entity(entity_type, entity_id)}/links", json=body)


def delete_link(entity_type: str, entity_id: str, right: str) -> Endpoint[None]:
    path = f"{_entity(entity_type, entity_id)}/links"
    return Endpoint("DELETE", path, params={"right": right})


# ---- attachments ---------------------------------------------------------------------------


def list_attachments(entity_type: str, entity_id: str) -> Endpoint[ItemList[Attachment]]:
    return Endpoint("GET", f"{_entity(entity_type, entity_id)}/attachments", ItemList[Attachment])


def get_attachment(entity_type: str, entity_id: str, file_id: str) -> Endpoint[Attachment]:
    path = f"{_entity(entity_type, entity_id)}/attachments/{segment(file_id)}"
    return Endpoint("GET", path, Attachment)


def download_attachment(file_id: str, filename: str) -> Endpoint[bytes]:
    return Endpoint("GET", f"attachments/{segment(file_id)}/{segment(filename)}", bytes)


def attach_file(
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


def delete_attachment(entity_type: str, entity_id: str, file_id: str) -> Endpoint[None]:
    """``DELETE …/attachments/{file_id}`` answers with an empty body."""
    path = f"{_entity(entity_type, entity_id)}/attachments/{segment(file_id)}"
    return Endpoint("DELETE", path)
