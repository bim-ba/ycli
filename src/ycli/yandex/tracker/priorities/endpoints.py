"""Tracker ``/priorities`` operations, declared once (sans-IO).

Examples:
    >>> update_priority("one", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.priorities.models import Priority, PriorityCreate, PriorityUpdate


def list_priorities(*, localized: bool | None) -> Endpoint[ItemList[Priority]]:
    return Endpoint("GET", "priorities", ItemList[Priority], params={"localized": localized})


def create_priority(body: PriorityCreate) -> Endpoint[Priority]:
    return Endpoint("POST", "priorities/", Priority, json=body)


def update_priority(
    priority_id: str, body: PriorityUpdate, *, version: int | None = None
) -> Endpoint[Priority]:
    """``PATCH /priorities/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH",
        f"priorities/{segment(priority_id)}",
        Priority,
        json=body,
        params={"version": version},
    )
