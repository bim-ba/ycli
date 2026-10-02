"""Tracker ``/queues`` and ``/versions`` operations, each declared once (sans-IO).

Example:
    >>> get_queue("TEST", expand="all").params
    {'expand': 'all'}
    >>> remove_tag("TEST", {"tag": "old"}).effect
    'destructive'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import PageNumberPagination
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueFieldList,
    QueueGroupAccess,
    QueueList,
    QueuePermissions,
    QueueTagList,
    QueueUserAccess,
    QueueVersionInfo,
    QueueVersionInfoList,
)

# Tracker's own default page size for /queues/.
PAGE_SIZE = 50


def _queue(queue_id: str) -> str:
    return f"queues/{segment(queue_id)}"


def list_queues() -> Paged[QueueList, Queue]:
    """``GET /queues/`` paged by ``page``/``perPage``.

    The trailing slash matters: without it Tracker answers with the queue whose key is empty.
    """
    return Paged(
        Endpoint("GET", "queues/", QueueList),
        PageNumberPagination(page_size=PAGE_SIZE),
        lambda page: page.root,
    )


def get_queue(queue_id: str, *, expand: str | None = None) -> Endpoint[Queue]:
    return Endpoint("GET", _queue(queue_id), Queue, params={"expand": expand})


def list_tags(queue_id: str) -> Endpoint[QueueTagList]:
    return Endpoint("GET", f"{_queue(queue_id)}/tags", QueueTagList)


def list_versions(queue_id: str) -> Endpoint[QueueVersionInfoList]:
    return Endpoint("GET", f"{_queue(queue_id)}/versions", QueueVersionInfoList)


def list_fields(queue_id: str) -> Endpoint[QueueFieldList]:
    return Endpoint("GET", f"{_queue(queue_id)}/fields", QueueFieldList)


def create_queue(body: dict[str, Any]) -> Endpoint[Queue]:
    return Endpoint("POST", "queues/", Queue, json=body)


def delete_queue(queue_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", _queue(queue_id))


def restore_queue(queue_id: str) -> Endpoint[Queue]:
    return Endpoint("POST", f"{_queue(queue_id)}/_restore", Queue)


def set_permissions(queue_id: str, body: dict[str, Any]) -> Endpoint[QueuePermissions]:
    return Endpoint("PATCH", f"{_queue(queue_id)}/permissions", QueuePermissions, json=body)


def remove_tag(queue_id: str, body: dict[str, Any]) -> Endpoint[None]:
    """``POST /queues/{id}/tags/_remove`` — strips the tag from every issue of the queue."""
    return Endpoint("POST", f"{_queue(queue_id)}/tags/_remove", json=body, effect="destructive")


def create_version(body: dict[str, Any]) -> Endpoint[QueueVersionInfo]:
    return Endpoint("POST", "versions/", QueueVersionInfo, json=body)


def get_version(version_id: int, *, fields: str | None = None) -> Endpoint[QueueVersionInfo]:
    return Endpoint(
        "GET", f"versions/{segment(version_id)}", QueueVersionInfo, params={"fields": fields}
    )


def edit_version(
    version_id: int, body: dict[str, Any], *, fields: str | None = None
) -> Endpoint[QueueVersionInfo]:
    """``PATCH /versions/{id}``: unlike a component, a version takes no ``?version=`` lock."""
    return Endpoint(
        "PATCH",
        f"versions/{segment(version_id)}",
        QueueVersionInfo,
        json=body,
        params={"fields": fields},
    )


def delete_version(version_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"versions/{segment(version_id)}")


def get_user_access(queue_id: str, user_id: str) -> Endpoint[QueueUserAccess]:
    path = f"{_queue(queue_id)}/permissions/users/{segment(user_id)}"
    return Endpoint("GET", path, QueueUserAccess)


def get_group_access(queue_id: str, group_id: int) -> Endpoint[QueueGroupAccess]:
    path = f"{_queue(queue_id)}/permissions/groups/{segment(group_id)}"
    return Endpoint("GET", path, QueueGroupAccess)
