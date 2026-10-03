"""Tracker ``/issues`` operations, each declared once (sans-IO, shared by sync and async).

Examples:
    >>> get_issue("TEST-1").path
    'issues/TEST-1'
    >>> search_issues({"query": "Queue: TEST"}).endpoint.effect
    'read'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import PageNumberPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.issues.models import Issue

# Tracker answers 50 per page by default; 100 halves the round trips of a long listing.
SEARCH_PAGE_SIZE = 100


def get_issue(key: str) -> Endpoint[Issue]:
    return Endpoint("GET", f"issues/{segment(key)}", Issue)


def search_issues(
    body: dict[str, Any], *, page_size: int = SEARCH_PAGE_SIZE
) -> Paged[ItemList[Issue], Issue]:
    """``POST /issues/_search`` with a ``filter`` or ``query`` body, paged by ``page``/``perPage``.

    Page-number paging covers up to 10 000 results; Tracker's scroll mode for more is not wired.
    """
    return Paged(
        Endpoint("POST", "issues/_search", ItemList[Issue], json=body, effect="read"),
        PageNumberPagination(page_size=page_size),
        lambda page: page.root,
    )


def count_issues(body: dict[str, Any]) -> Endpoint[int]:
    return Endpoint("POST", "issues/_count", int, json=body, effect="read")


def create_issue(body: dict[str, Any]) -> Endpoint[Issue]:
    return Endpoint("POST", "issues/", Issue, json=body)


def update_issue(key: str, body: dict[str, Any]) -> Endpoint[Issue]:
    return Endpoint("PATCH", f"issues/{segment(key)}", Issue, json=body)


def move_issue(key: str, queue: str) -> Endpoint[Issue]:
    return Endpoint("POST", f"issues/{segment(key)}/_move", Issue, params={"queue": queue})


def suggest_issues(text: str) -> Endpoint[ItemList[Issue]]:
    return Endpoint("GET", "issues/_suggest", ItemList[Issue], params={"input": text})


def clear_scroll(body: dict[str, str]) -> Endpoint[None]:
    """``POST /system/search/scroll/_clear`` — releasing a scroll is safe to repeat."""
    return Endpoint("POST", "system/search/scroll/_clear", json=body, effect="idempotent_write")
