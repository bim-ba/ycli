"""Wiki ``/pages``, declared once (sans-IO).

The API updates a page with ``POST /pages/{id}`` (``PATCH`` answers 405); sending the same body
twice leaves the same page, so that endpoint declares itself an idempotent write.

Examples:
    >>> get("data/x", fields=None, revision_id=None, raise_on_redirect=False).params
    {'slug': 'data/x', 'fields': None, 'revision_id': None, 'raise_on_redirect': False}
    >>> update(7, {"content": "# X"}, fields=None, is_silent=False, allow_merge=False).effect
    <Effect.IDEMPOTENT_WRITE: 'idempotent_write'>
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Effect, Endpoint, Paged, segment
from ycli.yandex.wiki.cursor import WIKI_CURSOR
from ycli.yandex.wiki.models import AsyncOperation, CursorPage
from ycli.yandex.wiki.pages.models import (
    GridRef,
    PageAppendContent,
    PageClone,
    PageCreate,
    PageDeleteResult,
    PageDetails,
    PageMove,
    PageRef,
    PageRevision,
    PageUpdate,
    SearchPage,
    SearchRequest,
)


def get(
    slug: str, *, fields: str | None, revision_id: int | None, raise_on_redirect: bool | None
) -> Endpoint[PageDetails]:
    params = {
        "slug": slug,
        "fields": fields,
        "revision_id": revision_id,
        "raise_on_redirect": raise_on_redirect,
    }
    return Endpoint(HTTPMethod.GET, "pages", PageDetails, params=params)


def get_by_id(
    page_id: int, *, fields: str | None, revision_id: int | None, raise_on_redirect: bool | None
) -> Endpoint[PageDetails]:
    params = {
        "fields": fields,
        "revision_id": revision_id,
        "raise_on_redirect": raise_on_redirect,
    }
    return Endpoint(HTTPMethod.GET, f"pages/{segment(page_id)}", PageDetails, params=params)


def descendants_list(
    slug: str, *, actuality: str | None, include_self: bool | None, show_all: bool | None
) -> Paged[CursorPage[PageRef], PageRef]:
    params = {
        "slug": slug,
        "page_size": 100,
        "actuality": actuality,
        "include_self": include_self,
        "show_all": show_all,
    }
    return Paged(
        Endpoint(HTTPMethod.GET, "pages/descendants", CursorPage[PageRef], params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def descendants_list_by_id(
    page_id: int, *, actuality: str | None, include_self: bool | None, show_all: bool | None
) -> Paged[CursorPage[PageRef], PageRef]:
    path = f"pages/{segment(page_id)}/descendants"
    params = {
        "page_size": 100,
        "actuality": actuality,
        "include_self": include_self,
        "show_all": show_all,
    }
    return Paged(
        Endpoint(HTTPMethod.GET, path, CursorPage[PageRef], params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def grids_list(
    page_id: int, *, order_by: str | None, order_direction: str | None
) -> Paged[CursorPage[GridRef], GridRef]:
    params = {"page_size": 50, "order_by": order_by, "order_direction": order_direction}
    return Paged(
        Endpoint(
            HTTPMethod.GET, f"pages/{segment(page_id)}/grids", CursorPage[GridRef], params=params
        ),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def create(
    body: PageCreate, *, fields: str | None, is_silent: bool | None
) -> Endpoint[PageDetails]:
    params = {"fields": fields, "is_silent": is_silent}
    return Endpoint(HTTPMethod.POST, "pages", PageDetails, params=params, json=body)


def update(
    page_id: int,
    body: PageUpdate,
    *,
    fields: str | None,
    is_silent: bool | None,
    allow_merge: bool | None,
) -> Endpoint[PageDetails]:
    path = f"pages/{segment(page_id)}"
    params = {"fields": fields, "is_silent": is_silent, "allow_merge": allow_merge}
    # violation(arch-3): POST /pages/{id} replaces fields; a resend is a no-op
    return Endpoint(
        HTTPMethod.POST, path, PageDetails, params=params, json=body, effect=Effect.IDEMPOTENT_WRITE
    )


def delete(page_id: int, *, recursive: bool | None) -> Endpoint[PageDeleteResult]:
    params = {"recursive": recursive}
    return Endpoint(HTTPMethod.DELETE, f"pages/{segment(page_id)}", PageDeleteResult, params=params)


def append(
    page_id: int, body: PageAppendContent, *, fields: str | None, is_silent: bool | None
) -> Endpoint[PageDetails]:
    path = f"pages/{segment(page_id)}/append-content"
    params = {"fields": fields, "is_silent": is_silent}
    return Endpoint(HTTPMethod.POST, path, PageDetails, params=params, json=body)


def clone(page_id: int, body: PageClone) -> Endpoint[AsyncOperation]:
    return Endpoint(HTTPMethod.POST, f"pages/{segment(page_id)}/clone", AsyncOperation, json=body)


def move(body: PageMove, *, validate_only: bool | None) -> Endpoint[AsyncOperation]:
    """``POST /pages/move`` (undocumented): a new address for pages, or only a check of one."""
    params = {"dry_run": validate_only}
    return Endpoint(HTTPMethod.POST, "pages/move", AsyncOperation, params=params, json=body)


def revisions_list(
    page_id: int, *, ids: str | None
) -> Paged[CursorPage[PageRevision], PageRevision]:
    """``GET /pages/{id}/revisions`` (undocumented): newest-first revisions, 50 a page at most."""
    params = {"page_size": 50, "ids": ids}
    return Paged(
        Endpoint(
            HTTPMethod.GET,
            f"pages/{segment(page_id)}/revisions",
            CursorPage[PageRevision],
            params=params,
        ),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def backlinks_list(
    page_id: int, *, for_cluster: bool | None, show_all: bool | None
) -> Paged[CursorPage[PageRef], PageRef]:
    """``GET /pages/{id}/backlinks`` (undocumented): the pages that link to this one."""
    params = {
        "page_size": 100,
        "for_cluster": for_cluster,
        "show_all": show_all,
    }
    return Paged(
        Endpoint(
            HTTPMethod.GET,
            f"pages/{segment(page_id)}/backlinks",
            CursorPage[PageRef],
            params=params,
        ),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def search(body: SearchRequest) -> Endpoint[SearchPage]:
    """``POST /search`` only reads: one page of full-text hits."""
    # violation(arch-3): POST /search only reads
    return Endpoint(HTTPMethod.POST, "search", SearchPage, json=body, effect=Effect.READ)
