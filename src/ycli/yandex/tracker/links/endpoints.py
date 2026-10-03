"""Tracker issue ``/links`` operations, declared once (sans-IO).

Examples:
    >>> delete_link("DE-130", "42").path
    'issues/DE-130/links/42'
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import PageNumberPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.links.models import Link, LinkPage

if TYPE_CHECKING:
    from collections.abc import Sequence

PAGE_SIZE = 50


def list_links(key: str) -> Endpoint[ItemList[Link]]:
    return Endpoint("GET", f"issues/{segment(key)}/links", ItemList[Link])


def search_links(
    key: str, *, link_types: Sequence[str] | None = None, fields: Sequence[str] | None = None
) -> Paged[LinkPage, Link]:
    """``POST /issues/{key}/links/_list`` only reads: a page of links, filtered by the body."""
    body = {"fields": fields, "linkTypes": link_types}
    return Paged(
        Endpoint(
            "POST",
            f"issues/{segment(key)}/links/_list",
            LinkPage,
            json={name: value for name, value in body.items() if value is not None},
            effect="read",
        ),
        PageNumberPagination(page_size=PAGE_SIZE),
        lambda page: page.links,
    )


def add_link(key: str, body: dict[str, Any]) -> Endpoint[Link]:
    return Endpoint("POST", f"issues/{segment(key)}/links", Link, json=body)


def delete_link(key: str, link_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(key)}/links/{segment(link_id)}")
