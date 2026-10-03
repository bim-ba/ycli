"""Tracker saved ``/filters`` operations, declared once (sans-IO).

Examples:
    >>> update_filter("12345", {"name": "Renamed"}).method
    'PATCH'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.filters.models import Filter, FilterCreate, FilterUpdate


def get_filter(filter_id: str) -> Endpoint[Filter]:
    return Endpoint("GET", f"filters/{segment(filter_id)}", Filter)


def create_filter(body: FilterCreate) -> Endpoint[Filter]:
    return Endpoint("POST", "filters/", Filter, json=body)


def update_filter(filter_id: str, body: FilterUpdate) -> Endpoint[Filter]:
    """``PATCH /filters/{id}``: no ``?version=`` lock; ``filter`` is replaced, not merged."""
    return Endpoint("PATCH", f"filters/{segment(filter_id)}", Filter, json=body)


def delete_filter(filter_id: str) -> Endpoint[None]:
    """``DELETE /filters/{id}``: the docs print ``/v2/``; the v3 route deletes it (checked live)."""
    return Endpoint("DELETE", f"filters/{segment(filter_id)}")
