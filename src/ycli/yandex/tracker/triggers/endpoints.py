"""Tracker queue ``/triggers`` operations, declared once (sans-IO).

Examples:
    >>> edit_trigger("DESIGN", 16, {"active": False}, version=2).params
    {'version': 2}
    >>> list_webhook_log("DEV", 6, limit=100).path
    'queues/DEV/triggers/6/webhooks/log'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIdPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.triggers.models import Trigger, WebhookLogEntry

PAGE_SIZE = 50


def _trigger_id(trigger: Trigger) -> str | None:
    return str(trigger.id) if trigger.id is not None else None


def _trigger_path(queue_id: str, trigger_id: int) -> str:
    return f"queues/{segment(queue_id)}/triggers/{segment(trigger_id)}"


def list_triggers(
    queue_id: str, *, page_size: int = PAGE_SIZE
) -> Paged[ItemList[Trigger], Trigger]:
    """``GET /queues/{id}/triggers``, ascending by id, each next page from ``id=<last id>``."""
    return Paged(
        Endpoint(
            "GET",
            f"queues/{segment(queue_id)}/triggers",
            ItemList[Trigger],
            params={"perPage": page_size},
        ),
        RelativeIdPagination(id_of=_trigger_id),
        lambda page: page.root,
    )


def get_trigger(queue_id: str, trigger_id: int) -> Endpoint[Trigger]:
    return Endpoint("GET", _trigger_path(queue_id, trigger_id), Trigger)


def create_trigger(queue_id: str, body: dict[str, Any]) -> Endpoint[Trigger]:
    return Endpoint("POST", f"queues/{segment(queue_id)}/triggers", Trigger, json=body)


def edit_trigger(
    queue_id: str, trigger_id: int, body: dict[str, Any], *, version: int | None
) -> Endpoint[Trigger]:
    path = _trigger_path(queue_id, trigger_id)
    return Endpoint("PATCH", path, Trigger, json=body, params={"version": version})


def list_webhook_log(
    queue_id: str,
    trigger_id: int,
    *,
    issue_id: str | None = None,
    limit: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> Endpoint[ItemList[WebhookLogEntry]]:
    """The Webhook-action run log (API default 10 records, ``limit`` up to 100)."""
    params = {"issueId": issue_id, "limit": limit, "from": date_from, "to": date_to}
    path = f"{_trigger_path(queue_id, trigger_id)}/webhooks/log"
    return Endpoint("GET", path, ItemList[WebhookLogEntry], params=params)
