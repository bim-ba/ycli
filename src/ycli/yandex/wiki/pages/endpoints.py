"""Wiki ``/pages``, declared once (sans-IO).

The API updates a page with ``POST /pages/{id}`` (``PATCH`` answers 405); sending the same body
twice leaves the same page, so that endpoint declares itself an idempotent write.

Example:
    >>> get_page("data/x", fields=None).params
    {'slug': 'data/x', 'fields': None}
    >>> update_page(7, {"content": "# X"}).effect
    'idempotent_write'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.cursor import WIKI_CURSOR
from ycli.yandex.wiki.pages.models import (
    DescendantsResponse,
    GridRef,
    GridsResponse,
    PageCloneOperation,
    PageDeleteResult,
    PageDetails,
    PageRef,
)


def get_page(slug: str, *, fields: str | None) -> Endpoint[PageDetails]:
    return Endpoint("GET", "pages", PageDetails, params={"slug": slug, "fields": fields})


def get_page_by_id(page_id: int, *, fields: str | None) -> Endpoint[PageDetails]:
    return Endpoint("GET", f"pages/{segment(page_id)}", PageDetails, params={"fields": fields})


def list_descendants(slug: str, *, actuality: str | None) -> Paged[DescendantsResponse, PageRef]:
    params = {"slug": slug, "page_size": 100, "actuality": actuality}
    return Paged(
        Endpoint("GET", "pages/descendants", DescendantsResponse, params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def list_descendants_by_id(
    page_id: int, *, actuality: str | None
) -> Paged[DescendantsResponse, PageRef]:
    path = f"pages/{segment(page_id)}/descendants"
    params = {"page_size": 100, "actuality": actuality}
    return Paged(
        Endpoint("GET", path, DescendantsResponse, params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def list_grids(page_id: int, *, order_by: str | None) -> Paged[GridsResponse, GridRef]:
    params = {"page_size": 50, "order_by": order_by}
    return Paged(
        Endpoint("GET", f"pages/{segment(page_id)}/grids", GridsResponse, params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def create_page(body: dict[str, Any]) -> Endpoint[PageDetails]:
    return Endpoint("POST", "pages", PageDetails, json=body)


def update_page(page_id: int, body: dict[str, Any]) -> Endpoint[PageDetails]:
    path = f"pages/{segment(page_id)}"
    return Endpoint("POST", path, PageDetails, json=body, effect="idempotent_write")


def delete_page(page_id: int) -> Endpoint[PageDeleteResult]:
    return Endpoint("DELETE", f"pages/{segment(page_id)}", PageDeleteResult)


def append_content(page_id: int, body: dict[str, Any]) -> Endpoint[PageDetails]:
    return Endpoint("POST", f"pages/{segment(page_id)}/append-content", PageDetails, json=body)


def clone_page(page_id: int, body: dict[str, Any]) -> Endpoint[PageCloneOperation]:
    return Endpoint("POST", f"pages/{segment(page_id)}/clone", PageCloneOperation, json=body)
