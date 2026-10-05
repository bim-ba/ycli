"""Tracker saved ``/filters`` operations, declared once (sans-IO).

Examples:
    >>> update("12345", {"name": "Renamed"}).method
    <HTTPMethod.PATCH>
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate


def get(filter_id: str) -> Endpoint[Filter]:
    return Endpoint(HTTPMethod.GET, f"filters/{segment(filter_id)}", Filter)


def create(body: FilterCreate) -> Endpoint[Filter]:
    return Endpoint(HTTPMethod.POST, "filters/", Filter, json=body)


def update(filter_id: str, body: FilterUpdate) -> Endpoint[Filter]:
    """``PATCH /filters/{id}``: no ``?version=`` lock; ``filter`` is replaced, not merged."""
    return Endpoint(HTTPMethod.PATCH, f"filters/{segment(filter_id)}", Filter, json=body)


def delete(filter_id: str) -> Endpoint[None]:
    """``DELETE /filters/{id}``: the docs print ``/v2/``; the v3 route deletes it (checked live)."""
    return Endpoint(HTTPMethod.DELETE, f"filters/{segment(filter_id)}")
