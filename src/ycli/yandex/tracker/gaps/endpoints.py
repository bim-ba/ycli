"""Tracker ``/gaps`` operations (employee absences; admin-only), each declared once (sans-IO).

Examples:
    >>> delete(["g1", "g2"]).params
    {'gapIds': 'g1,g2'}
    >>> search({"users": ["ann"]}).endpoint.effect
    'read'
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.core.pagination import PageNumberPagination
from ycli.yandex.tracker.gaps.models import GapCreated, GapsCreate, GapSearchPage, UserGaps

if TYPE_CHECKING:
    from collections.abc import Sequence

# ``perPage`` counts users, not absences; the API's own default is 50.
PAGE_SIZE = 50


def create(body: GapsCreate) -> Endpoint[GapCreated]:
    return Endpoint("POST", "gaps", GapCreated, json=body)


def search(body: dict[str, Any]) -> Paged[GapSearchPage, UserGaps]:
    """``POST /gaps/_search`` only reads; pages of users, each next page from ``page=``."""
    return Paged(
        # violation(arch-3): POST _search only reads
        Endpoint("POST", "gaps/_search", GapSearchPage, json=body, effect="read"),
        PageNumberPagination(page_size=PAGE_SIZE),
        lambda page: page.user_gaps,
    )


def delete(gap_ids: Sequence[str]) -> Endpoint[None]:
    """``DELETE /gaps?gapIds=a,b`` — ids the API does not know are ignored."""
    return Endpoint("DELETE", "gaps", params={"gapIds": ",".join(gap_ids)})
