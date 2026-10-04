"""Forms ``/notifications`` operations, declared once (sans-IO).

Examples:
    >>> restart(7).path
    'notifications/7/restart'
    >>> filters = NotificationFilter(survey_id="686d", status=["error"])
    >>> list_(filters).endpoint.params["status"]
    ['error']
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import NextURLPagination
from ycli.yandex.forms.notifications.models import (
    Notification,
    NotificationAction,
    NotificationDetails,
    NotificationFilter,
    NotificationPage,
    NotificationStatus,
)
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    import httpx2

PAGE_SIZE = 100


def _next_link(response: httpx2.Response) -> str | None:
    return response.json().get("links", {}).get("next")


def list_(filters: NotificationFilter) -> Paged[NotificationPage, Notification]:
    """``GET /notifications``, paged by the ``links.next`` link.

    The link is a host-relative path that ends in a slash, so only its query (the ``id`` cursor
    plus the filters) is carried over onto the request.
    """
    params = {**filters.params(), "page_size": PAGE_SIZE}
    return Paged(
        Endpoint("GET", "notifications", NotificationPage, params=params),
        NextURLPagination(url_of=_next_link, query_only=True),
        lambda page: page.result,
    )


def get(notification_id: int) -> Endpoint[NotificationDetails]:
    return Endpoint("GET", f"notifications/{segment(notification_id)}", NotificationDetails)


def status_get(notification_id: int) -> Endpoint[NotificationStatus]:
    return Endpoint("GET", f"notifications/{segment(notification_id)}/status", NotificationStatus)


def restart(notification_id: int) -> Endpoint[NotificationAction]:
    path = f"notifications/{segment(notification_id)}/restart"
    return Endpoint("POST", path, NotificationAction)


def cancel(notification_id: int) -> Endpoint[NotificationAction]:
    path = f"notifications/{segment(notification_id)}/cancel"
    return Endpoint("POST", path, NotificationAction)


def errors_list(survey_id: str) -> Endpoint[ItemList[int]]:
    return Endpoint("GET", f"surveys/{segment(survey_id)}/show-errors", ItemList[int])
