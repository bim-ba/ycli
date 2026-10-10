"""Tracker queue ``/triggers`` operations, declared once (sans-IO).

Examples:
    >>> update("DESIGN", 16, {"active": False}, version=2).params
    {'version': 2}
    >>> webhook_log_list("DEV", 6, limit=100).path
    'queues/DEV/triggers/6/webhooks/log'
"""

from http import HTTPMethod
from typing import Annotated

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.models import ItemList
from ycli.yandex.sync.marks import Container, Identity, Version
from ycli.yandex.tracker import queues
from ycli.yandex.tracker.triggers.models import (
    Trigger,
    TriggerCreate,
    TriggerUpdate,
    WebhookLogEntry,
)

PAGE_SIZE = 50


def _trigger_id(trigger: Trigger) -> str | None:
    return str(trigger.id) if trigger.id is not None else None


def _trigger_path(queue_id: str, trigger_id: int) -> str:
    return f"queues/{segment(queue_id)}/triggers/{segment(trigger_id)}"


def list_(
    queue_id: Annotated[str, Container(queues)], *, page_size: int = PAGE_SIZE
) -> Paged[ItemList[Trigger], Trigger]:
    """``GET /queues/{id}/triggers``, ascending by id, each next page from ``id=<last id>``."""
    return Paged(
        Endpoint(
            HTTPMethod.GET,
            f"queues/{segment(queue_id)}/triggers",
            ItemList[Trigger],
        ),
        RelativeIDPagination(id_of=_trigger_id, page_size=page_size),
        lambda page: page.root,
    )


def get(
    queue_id: Annotated[str, Container(queues)], trigger_id: Annotated[int, Identity()]
) -> Endpoint[Trigger]:
    return Endpoint(HTTPMethod.GET, _trigger_path(queue_id, trigger_id), Trigger)


def create(queue_id: Annotated[str, Container(queues)], body: TriggerCreate) -> Endpoint[Trigger]:
    return Endpoint(HTTPMethod.POST, f"queues/{segment(queue_id)}/triggers", Trigger, json=body)


def update(
    queue_id: Annotated[str, Container(queues)],
    trigger_id: Annotated[int, Identity()],
    body: TriggerUpdate,
    *,
    version: Annotated[int | None, Version()],
) -> Endpoint[Trigger]:
    path = _trigger_path(queue_id, trigger_id)
    return Endpoint(HTTPMethod.PATCH, path, Trigger, json=body, params={"version": version})


def webhook_log_list(
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
    return Endpoint(HTTPMethod.GET, path, ItemList[WebhookLogEntry], params=params)
