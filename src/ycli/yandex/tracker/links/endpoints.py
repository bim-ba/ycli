"""Tracker issue ``/links`` operations, declared once (sans-IO).

Examples:
    >>> delete("DE-130", "42").path
    'issues/DE-130/links/42'
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import PageNumberPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.links.models import ImportLink, Link, LinkCreate, LinkPage

if TYPE_CHECKING:
    from collections.abc import Sequence

PAGE_SIZE = 50


def list_(key: str) -> Endpoint[ItemList[Link]]:
    return Endpoint("GET", f"issues/{segment(key)}/links", ItemList[Link])


def list_filtered(
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


def create(key: str, body: LinkCreate) -> Endpoint[Link]:
    return Endpoint("POST", f"issues/{segment(key)}/links", Link, json=body)


def delete(key: str, link_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(key)}/links/{segment(link_id)}")


def import_(issue_key: str, body: ImportLink) -> Endpoint[Link]:
    return Endpoint("POST", f"issues/{segment(issue_key)}/links/_import", Link, json=body)
