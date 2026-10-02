"""Forms ``/surveys/{id}/history`` operation, declared once (sans-IO).

Example:
    >>> list_history("686d", ordering="asc").endpoint.params
    {'ordering': 'asc', 'limit': 100}
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import CursorPagination
from ycli.yandex.forms.history.models import HistoryEvent, HistoryPage

if TYPE_CHECKING:
    import httpx2

PAGE_SIZE = 100


def _iteration_key(response: httpx2.Response) -> str | None:
    key = response.json().get("iteration_key")
    return None if key is None else str(key)


def list_history(survey_id: str, *, ordering: str | None) -> Paged[HistoryPage, HistoryEvent]:
    """``GET /surveys/{id}/history``, paged by sending back the ``iteration_key`` cursor."""
    params = {"ordering": ordering, "limit": PAGE_SIZE}
    return Paged(
        Endpoint("GET", f"surveys/{segment(survey_id)}/history", HistoryPage, params=params),
        CursorPagination(cursor_of=_iteration_key, cursor_param="iteration_key"),
        lambda page: page.items,
    )
