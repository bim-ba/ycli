"""Tracker ``/statuses`` operations, declared once (sans-IO).

Example:
    >>> edit_status("29", {"description": "x"}, version=1).params
    {'version': 1}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.statuses.models import Status, StatusList


def list_statuses() -> Endpoint[StatusList]:
    return Endpoint("GET", "statuses", StatusList)


def create_status(body: dict[str, Any]) -> Endpoint[Status]:
    return Endpoint("POST", "statuses/", Status, json=body)


def edit_status(
    status_id: str, body: dict[str, Any], *, version: int | None = None
) -> Endpoint[Status]:
    """``PATCH /statuses/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH", f"statuses/{segment(status_id)}", Status, json=body, params={"version": version}
    )
