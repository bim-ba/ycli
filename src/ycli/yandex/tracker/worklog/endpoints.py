"""Tracker worklog operations, declared once (sans-IO).

Examples:
    >>> search_worklog({"createdBy": "alice"}).effect
    'read'
    >>> list_global_worklog("alice", ["from:2018-06-06", "to:2018-06-07"]).params["createdAt"]
    ['from:2018-06-06', 'to:2018-06-07']
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIdPagination
from ycli.yandex.tracker.worklog.models import Worklog, WorklogList

if TYPE_CHECKING:
    from collections.abc import Sequence

PAGE_SIZE = 100


def _record_id(record: Worklog) -> str | None:
    return str(record.id) if record.id is not None else None


def list_worklog(key: str, *, page_size: int = PAGE_SIZE) -> Paged[WorklogList, Worklog]:
    """``GET /issues/{key}/worklog``: ascending ids, each next page from ``id=<last record>``."""
    return Paged(
        Endpoint(
            "GET", f"issues/{segment(key)}/worklog", WorklogList, params={"perPage": page_size}
        ),
        RelativeIdPagination(id_of=_record_id),
        lambda page: page.root,
    )


def search_worklog(body: dict[str, Any]) -> Endpoint[WorklogList]:
    """``POST /worklog/_search`` only reads."""
    return Endpoint("POST", "worklog/_search", WorklogList, json=body, effect="read")


def list_global_worklog(
    created_by: str | None, created_at: Sequence[str] | str | None
) -> Endpoint[WorklogList]:
    """``GET /worklog``; a list ``created_at`` repeats ``createdAt`` (``from:…``, ``to:…``)."""
    params = {"createdBy": created_by, "createdAt": created_at}
    return Endpoint("GET", "worklog", WorklogList, params=params)


def create_worklog(key: str, body: dict[str, Any]) -> Endpoint[Worklog]:
    return Endpoint("POST", f"issues/{segment(key)}/worklog", Worklog, json=body)


def edit_worklog(key: str, record_id: int | str, body: dict[str, Any]) -> Endpoint[Worklog]:
    path = f"issues/{segment(key)}/worklog/{segment(record_id)}"
    return Endpoint("PATCH", path, Worklog, json=body)


def delete_worklog(key: str, record_id: int | str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(key)}/worklog/{segment(record_id)}")
