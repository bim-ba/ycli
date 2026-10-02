"""Tracker ``/priorities`` operations, declared once (sans-IO).

Examples:
    >>> edit_priority("one", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.priorities.models import Priority, PriorityList


def list_priorities() -> Endpoint[PriorityList]:
    return Endpoint("GET", "priorities", PriorityList)


def create_priority(body: dict[str, Any]) -> Endpoint[Priority]:
    return Endpoint("POST", "priorities/", Priority, json=body)


def edit_priority(
    priority_id: str, body: dict[str, Any], *, version: int | None = None
) -> Endpoint[Priority]:
    """``PATCH /priorities/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH",
        f"priorities/{segment(priority_id)}",
        Priority,
        json=body,
        params={"version": version},
    )
