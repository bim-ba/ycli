"""Tracker ``/statuses`` operations, declared once (sans-IO).

Examples:
    >>> update_status("29", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.statuses.models import Status, StatusCreate, StatusUpdate


def list_statuses() -> Endpoint[ItemList[Status]]:
    return Endpoint("GET", "statuses", ItemList[Status])


def create_status(body: StatusCreate) -> Endpoint[Status]:
    return Endpoint("POST", "statuses/", Status, json=body)


def update_status(
    status_id: str, body: StatusUpdate, *, version: int | None = None
) -> Endpoint[Status]:
    """``PATCH /statuses/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH", f"statuses/{segment(status_id)}", Status, json=body, params={"version": version}
    )
