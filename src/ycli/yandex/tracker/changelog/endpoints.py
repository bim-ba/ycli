"""Tracker issue ``/changelog`` listing, declared once (sans-IO).

Examples:
    >>> paged = list_("DE-1", field=None, change_type=None, sort=None, page_size=5)
    >>> paged.endpoint.path
    'issues/DE-1/changelog'
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.changelog.models import ChangelogEntry

PAGE_SIZE = 100


def _entry_id(entry: ChangelogEntry) -> str | None:
    return entry.id


def list_(
    issue_key: str,
    *,
    field: str | None,
    change_type: str | None,
    sort: str | None,
    page_size: int = PAGE_SIZE,
) -> Paged[ItemList[ChangelogEntry], ChangelogEntry]:
    """``GET /issues/{key}/changelog``, each next page from ``id=<last change id>``."""
    return Paged(
        Endpoint(
            HTTPMethod.GET,
            f"issues/{segment(issue_key)}/changelog",
            ItemList[ChangelogEntry],
            params={"perPage": page_size, "field": field, "type": change_type, "sort": sort},
        ),
        RelativeIDPagination(id_of=_entry_id),
        lambda page: page.root,
    )
