"""Tracker ``/statuses`` operations, declared once (sans-IO).

Examples:
    >>> update("29", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.statuses.models import Status, StatusCreate, StatusUpdate


def list_() -> Endpoint[ItemList[Status]]:
    return Endpoint(HTTPMethod.GET, "statuses", ItemList[Status])


def create(body: StatusCreate) -> Endpoint[Status]:
    return Endpoint(HTTPMethod.POST, "statuses/", Status, json=body)


def update(status_id: str, body: StatusUpdate, *, version: int | None = None) -> Endpoint[Status]:
    """``PATCH /statuses/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"statuses/{segment(status_id)}",
        Status,
        json=body,
        params={"version": version},
    )
