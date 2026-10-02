"""Tracker issue ``/links`` operations, declared once (sans-IO).

Example:
    >>> delete_link("DE-130", "42").path
    'issues/DE-130/links/42'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.links.models import Link, LinkList


def list_links(key: str) -> Endpoint[LinkList]:
    return Endpoint("GET", f"issues/{segment(key)}/links", LinkList)


def add_link(key: str, body: dict[str, Any]) -> Endpoint[Link]:
    return Endpoint("POST", f"issues/{segment(key)}/links", Link, json=body)


def delete_link(key: str, link_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(key)}/links/{segment(link_id)}")
