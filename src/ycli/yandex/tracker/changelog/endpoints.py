"""Tracker issue ``/changelog`` listing, declared once (sans-IO).

Examples:
    >>> list_changelog("DE-1", page_size=5).endpoint.path
    'issues/DE-1/changelog'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIdPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.changelog.models import ChangelogEntry

PAGE_SIZE = 100


def _entry_id(entry: ChangelogEntry) -> str | None:
    return entry.id


def list_changelog(
    key: str, *, page_size: int = PAGE_SIZE
) -> Paged[ItemList[ChangelogEntry], ChangelogEntry]:
    """``GET /issues/{key}/changelog``, each next page from ``id=<last change id>``."""
    return Paged(
        Endpoint(
            "GET",
            f"issues/{segment(key)}/changelog",
            ItemList[ChangelogEntry],
            params={"perPage": page_size},
        ),
        RelativeIdPagination(id_of=_entry_id),
        lambda page: page.root,
    )
