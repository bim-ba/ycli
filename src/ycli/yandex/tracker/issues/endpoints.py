"""Tracker ``/issues`` operations, each declared once (sans-IO, shared by sync and async).

Examples:
    >>> get("TEST-1", expand=None, fields=None).path
    'issues/TEST-1'
    >>> search(IssueSearch(query="Queue: TEST"), expand=None).endpoint.effect
    'read'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import PageNumberPagination, ScrollPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.bulk.models import BulkChange, BulkMove, BulkTransition, BulkUpdate
from ycli.yandex.tracker.issues.models import (
    ImportTask,
    Issue,
    IssueCreate,
    IssueSearch,
    IssueUpdate,
    ScrollClear,
)

# Tracker answers 50 per page by default; 100 halves the round trips of a long listing.
SEARCH_PAGE_SIZE = 100


def get(
    issue_key: str,
    *,
    expand: str | None,
    fields: str | None,
) -> Endpoint[Issue]:
    return Endpoint(
        "GET", f"issues/{segment(issue_key)}", Issue, params={"expand": expand, "fields": fields}
    )


def search(
    body: IssueSearch, *, expand: str | None, page_size: int = SEARCH_PAGE_SIZE
) -> Paged[ItemList[Issue], Issue]:
    """``POST /issues/_search`` with a ``filter`` or ``query`` body, paged by ``page``/``perPage``.

    Page-number paging covers up to 10 000 results; :func:`search_scroll` reads more.
    """
    # violation(arch-3): POST _search only reads
    endpoint = Endpoint(
        "POST",
        "issues/_search",
        ItemList[Issue],
        params={"expand": expand},
        json=body,
        effect="read",
    )
    return Paged(endpoint, PageNumberPagination(page_size=page_size), lambda page: page.root)


def search_scroll(
    body: IssueSearch,
    *,
    expand: str | None,
    scroll_type: str,
    per_scroll: int | None,
    scroll_ttl_millis: int | None,
) -> Paged[ItemList[Issue], Issue]:
    """``POST /issues/_search`` in scroll mode: no 10 000 cap, each page named by the last reply.

    ``scroll_type`` is ``sorted`` (the order of the search) or ``unsorted``; ``per_scroll`` is
    the page size (1000 at most) and ``scroll_ttl_millis`` how long the scroll stays open.
    """
    params = {
        "expand": expand,
        "scrollType": scroll_type,
        "perScroll": per_scroll,
        "scrollTTLMillis": scroll_ttl_millis,
    }
    # violation(arch-3): POST _search only reads
    endpoint = Endpoint(
        "POST", "issues/_search", ItemList[Issue], params=params, json=body, effect="read"
    )
    return Paged(endpoint, ScrollPagination(), lambda page: page.root)


def count(body: IssueSearch) -> Endpoint[int]:
    # violation(arch-3): POST _count only reads
    return Endpoint("POST", "issues/_count", int, json=body, effect="read")


def create(
    body: IssueCreate,
    *,
    notify: bool | None,
) -> Endpoint[Issue]:
    return Endpoint("POST", "issues/", Issue, json=body, params={"notify": notify})


def update(issue_key: str, body: IssueUpdate) -> Endpoint[Issue]:
    return Endpoint("PATCH", f"issues/{segment(issue_key)}", Issue, json=body)


def move(
    issue_key: str,
    queue: str,
    *,
    expand: str | None,
    initial_status: bool | None,
    move_all_fields: bool | None,
    notify: bool | None,
    notify_author: bool | None,
) -> Endpoint[Issue]:
    params = {
        "queue": queue,
        "expand": expand,
        "initialStatus": initial_status,
        "moveAllFields": move_all_fields,
        "notify": notify,
        "notifyAuthor": notify_author,
    }
    return Endpoint("POST", f"issues/{segment(issue_key)}/_move", Issue, params=params)


def suggest(
    text: str,
    *,
    queue: str | None,
    full: bool | None,
    fields: str | None,
    expand: str | None,
    embed: str | None,
) -> Endpoint[ItemList[Issue]]:
    params = {
        "input": text,
        "queue": queue,
        "full": full,
        "fields": fields,
        "expand": expand,
        "embed": embed,
    }
    return Endpoint("GET", "issues/_suggest", ItemList[Issue], params=params)


def scroll_clear(body: ScrollClear) -> Endpoint[None]:
    """``POST /system/search/scroll/_clear`` — releasing a scroll is safe to repeat."""
    # violation(arch-3): releasing a scroll twice is harmless
    return Endpoint("POST", "system/search/scroll/_clear", json=body, effect="idempotent_write")


def update_bulk(
    body: BulkUpdate,
    *,
    notify: bool | None,
) -> Endpoint[BulkChange]:
    return Endpoint("POST", "bulkchange/_update", BulkChange, json=body, params={"notify": notify})


def move_bulk(
    body: BulkMove,
    *,
    notify: bool | None,
) -> Endpoint[BulkChange]:
    return Endpoint("POST", "bulkchange/_move", BulkChange, json=body, params={"notify": notify})


def transition_bulk(
    body: BulkTransition,
    *,
    notify: bool | None,
) -> Endpoint[BulkChange]:
    return Endpoint(
        "POST", "bulkchange/_transition", BulkChange, json=body, params={"notify": notify}
    )


def import_(body: ImportTask) -> Endpoint[Issue]:
    return Endpoint("POST", "issues/_import", Issue, json=body)
