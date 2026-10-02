"""Tracker saved ``/filters`` operations, declared once (sans-IO).

Example:
    >>> edit_filter("12345", {"name": "Renamed"}).method
    'PATCH'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.filters.models import Filter


def get_filter(filter_id: str) -> Endpoint[Filter]:
    return Endpoint("GET", f"filters/{segment(filter_id)}", Filter)


def create_filter(body: dict[str, Any]) -> Endpoint[Filter]:
    return Endpoint("POST", "filters/", Filter, json=body)


def edit_filter(filter_id: str, body: dict[str, Any]) -> Endpoint[Filter]:
    """``PATCH /filters/{id}``: no ``?version=`` lock; ``filter`` is replaced, not merged."""
    return Endpoint("PATCH", f"filters/{segment(filter_id)}", Filter, json=body)
