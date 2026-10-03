"""Wiki ``/pages``, declared once (sans-IO).

The API updates a page with ``POST /pages/{id}`` (``PATCH`` answers 405); sending the same body
twice leaves the same page, so that endpoint declares itself an idempotent write.

Examples:
    >>> get_page("data/x", fields=None).params
    {'slug': 'data/x', 'fields': None}
    >>> update_page(7, {"content": "# X"}).effect
    'idempotent_write'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.cursor import WIKI_CURSOR
from ycli.yandex.wiki.models import AsyncOperation, CursorPage
from ycli.yandex.wiki.pages.models import (
    GridRef,
    PageDeleteResult,
    PageDetails,
    PageRef,
    PageRevision,
)


def get_page(slug: str, *, fields: str | None) -> Endpoint[PageDetails]:
    return Endpoint("GET", "pages", PageDetails, params={"slug": slug, "fields": fields})


def get_page_by_id(page_id: int, *, fields: str | None) -> Endpoint[PageDetails]:
    return Endpoint("GET", f"pages/{segment(page_id)}", PageDetails, params={"fields": fields})


def list_descendants(slug: str, *, actuality: str | None) -> Paged[CursorPage[PageRef], PageRef]:
    params = {"slug": slug, "page_size": 100, "actuality": actuality}
    return Paged(
        Endpoint("GET", "pages/descendants", CursorPage[PageRef], params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def list_descendants_by_id(
    page_id: int, *, actuality: str | None
) -> Paged[CursorPage[PageRef], PageRef]:
    path = f"pages/{segment(page_id)}/descendants"
    params = {"page_size": 100, "actuality": actuality}
    return Paged(
        Endpoint("GET", path, CursorPage[PageRef], params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def list_grids(page_id: int, *, order_by: str | None) -> Paged[CursorPage[GridRef], GridRef]:
    params = {"page_size": 50, "order_by": order_by}
    return Paged(
        Endpoint("GET", f"pages/{segment(page_id)}/grids", CursorPage[GridRef], params=params),
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


def clone_page(page_id: int, body: dict[str, Any]) -> Endpoint[AsyncOperation]:
    return Endpoint("POST", f"pages/{segment(page_id)}/clone", AsyncOperation, json=body)


def move_pages(body: dict[str, Any], *, dry_run: bool) -> Endpoint[AsyncOperation]:
    """``POST /pages/move`` (undocumented): a new address for pages; ``dry_run`` only validates."""
    params = {"dry_run": "true" if dry_run else None}
    return Endpoint("POST", "pages/move", AsyncOperation, params=params, json=body)


def list_revisions(
    page_id: int, *, ids: str | None
) -> Paged[CursorPage[PageRevision], PageRevision]:
    """``GET /pages/{id}/revisions`` (undocumented): newest-first revisions, 50 a page at most."""
    params = {"page_size": 50, "ids": ids}
    return Paged(
        Endpoint(
            "GET", f"pages/{segment(page_id)}/revisions", CursorPage[PageRevision], params=params
        ),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def list_backlinks(
    page_id: int, *, for_cluster: bool, show_all: bool
) -> Paged[CursorPage[PageRef], PageRef]:
    """``GET /pages/{id}/backlinks`` (undocumented): the pages that link to this one."""
    params = {
        "page_size": 100,
        "for_cluster": "true" if for_cluster else None,
        "show_all": "true" if show_all else None,
    }
    return Paged(
        Endpoint("GET", f"pages/{segment(page_id)}/backlinks", CursorPage[PageRef], params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )
