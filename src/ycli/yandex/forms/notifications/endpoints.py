"""Forms ``/notifications`` operations, declared once (sans-IO).

Example:
    >>> restart_notification(7).path
    'notifications/7/restart'
    >>> list_notifications(survey_id="686d", status=["error"]).endpoint.params["status"]
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
    NotificationIdList,
    NotificationPage,
    NotificationStatus,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    import httpx2

PAGE_SIZE = 100


def _next_link(response: httpx2.Response) -> str | None:
    return response.json().get("links", {}).get("next")


def list_notifications(
    *,
    survey_id: str | None = None,
    hook_id: int | None = None,
    subscription_id: int | None = None,
    answer_id: int | None = None,
    status: Sequence[str] | None = None,
    created_since: str | None = None,
    created_until: str | None = None,
    finished_since: str | None = None,
    finished_until: str | None = None,
    visible: bool | None = None,
    integration_type: str | None = None,
    ordering: str | None = None,
) -> Paged[NotificationPage, Notification]:
    """``GET /notifications``, paged by the ``links.next`` link.

    The link is a host-relative path that ends in a slash, so only its query (the ``id`` cursor
    plus the filters) is carried over onto the request.
    """
    params = {
        "survey_id": survey_id,
        "hook_id": hook_id,
        "subscription_id": subscription_id,
        "answer_id": answer_id,
        "status": status,
        "created_gt": created_since,
        "created_lt": created_until,
        "finished_gt": finished_since,
        "finished_lt": finished_until,
        "visible": visible,
        "type": integration_type,
        "ordering": ordering,
        "page_size": PAGE_SIZE,
    }
    return Paged(
        Endpoint("GET", "notifications", NotificationPage, params=params),
        NextURLPagination(url_of=_next_link, query_only=True),
        lambda page: page.result,
    )


def get_notification(notification_id: int) -> Endpoint[NotificationDetails]:
    return Endpoint("GET", f"notifications/{segment(notification_id)}", NotificationDetails)


def get_notification_status(notification_id: int) -> Endpoint[NotificationStatus]:
    return Endpoint("GET", f"notifications/{segment(notification_id)}/status", NotificationStatus)


def restart_notification(notification_id: int) -> Endpoint[NotificationAction]:
    path = f"notifications/{segment(notification_id)}/restart"
    return Endpoint("POST", path, NotificationAction)


def cancel_notification(notification_id: int) -> Endpoint[NotificationAction]:
    path = f"notifications/{segment(notification_id)}/cancel"
    return Endpoint("POST", path, NotificationAction)


def list_failed_notifications(survey_id: str) -> Endpoint[NotificationIdList]:
    return Endpoint("GET", f"surveys/{segment(survey_id)}/show-errors", NotificationIdList)
