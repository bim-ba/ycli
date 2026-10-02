"""Tracker ``/resolutions`` operations, declared once (sans-IO).

Examples:
    >>> edit_resolution("9", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.resolutions.models import Resolution, ResolutionList


def list_resolutions() -> Endpoint[ResolutionList]:
    return Endpoint("GET", "resolutions", ResolutionList)


def create_resolution(body: dict[str, Any]) -> Endpoint[Resolution]:
    return Endpoint("POST", "resolutions/", Resolution, json=body)


def edit_resolution(
    resolution_id: str, body: dict[str, Any], *, version: int | None = None
) -> Endpoint[Resolution]:
    """``PATCH /resolutions/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH",
        f"resolutions/{segment(resolution_id)}",
        Resolution,
        json=body,
        params={"version": version},
    )
