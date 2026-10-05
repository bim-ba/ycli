"""Tracker ``/resolutions`` operations, declared once (sans-IO).

Examples:
    >>> update("9", {"description": "x"}, version=1).params
    {'version': 1}
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.resolutions.models import Resolution, ResolutionCreate, ResolutionUpdate


def list_() -> Endpoint[ItemList[Resolution]]:
    return Endpoint(HTTPMethod.GET, "resolutions", ItemList[Resolution])


def create(body: ResolutionCreate) -> Endpoint[Resolution]:
    return Endpoint(HTTPMethod.POST, "resolutions/", Resolution, json=body)


def update(
    resolution_id: str, body: ResolutionUpdate, *, version: int | None = None
) -> Endpoint[Resolution]:
    """``PATCH /resolutions/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"resolutions/{segment(resolution_id)}",
        Resolution,
        json=body,
        params={"version": version},
    )
