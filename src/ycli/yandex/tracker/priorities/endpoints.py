"""Tracker ``/priorities`` operations, declared once (sans-IO).

Examples:
    >>> update("one", {"description": "x"}, version=1).params
    {'version': 1}
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.priorities.models import Priority, PriorityCreate, PriorityUpdate


def list_(*, localized: bool | None) -> Endpoint[ItemList[Priority]]:
    return Endpoint(
        HTTPMethod.GET, "priorities", ItemList[Priority], params={"localized": localized}
    )


def create(body: PriorityCreate) -> Endpoint[Priority]:
    return Endpoint(HTTPMethod.POST, "priorities/", Priority, json=body)


def update(
    priority_id: str, body: PriorityUpdate, *, version: int | None = None
) -> Endpoint[Priority]:
    """``PATCH /priorities/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"priorities/{segment(priority_id)}",
        Priority,
        json=body,
        params={"version": version},
    )
