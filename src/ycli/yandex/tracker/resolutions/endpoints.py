"""Tracker ``/resolutions`` operations, declared once (sans-IO).

Examples:
    >>> update_resolution("9", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.resolutions.models import Resolution, ResolutionCreate, ResolutionUpdate


def list_resolutions() -> Endpoint[ItemList[Resolution]]:
    return Endpoint("GET", "resolutions", ItemList[Resolution])


def create_resolution(body: ResolutionCreate) -> Endpoint[Resolution]:
    return Endpoint("POST", "resolutions/", Resolution, json=body)


def update_resolution(
    resolution_id: str, body: ResolutionUpdate, *, version: int | None = None
) -> Endpoint[Resolution]:
    """``PATCH /resolutions/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH",
        f"resolutions/{segment(resolution_id)}",
        Resolution,
        json=body,
        params={"version": version},
    )
