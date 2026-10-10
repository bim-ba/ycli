"""Tracker worklog operations, declared once (sans-IO).

Examples:
    >>> search({"createdBy": "alice"}).effect
    <Effect.READ: 'read'>
    >>> list_global("alice", "2018-06-06", "2018-06-07").params["createdAt"]
    ['from:2018-06-06', 'to:2018-06-07']
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Effect, Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.worklog.models import (
    ImportWorklog,
    Worklog,
    WorklogCreate,
    WorklogSearch,
    WorklogUpdate,
)

PAGE_SIZE = 100


def _record_id(record: Worklog) -> str | None:
    return str(record.id) if record.id is not None else None


def list_(issue_key: str, *, page_size: int = PAGE_SIZE) -> Paged[ItemList[Worklog], Worklog]:
    """``GET /issues/{key}/worklog``: ascending ids, each next page from ``id=<last record>``."""
    return Paged(
        Endpoint(
            HTTPMethod.GET,
            f"issues/{segment(issue_key)}/worklog",
            ItemList[Worklog],
        ),
        RelativeIDPagination(id_of=_record_id, page_size=page_size),
        lambda page: page.root,
    )


def search(body: WorklogSearch) -> Endpoint[ItemList[Worklog]]:
    """``POST /worklog/_search`` only reads."""
    # violation(arch-3): POST _search only reads
    return Endpoint(
        HTTPMethod.POST, "worklog/_search", ItemList[Worklog], json=body, effect=Effect.READ
    )


def list_global(
    created_by: str | None, created_from: str | None, created_to: str | None
) -> Endpoint[ItemList[Worklog]]:
    """``GET /worklog``; each end of the range is one ``createdAt`` (``from:…``, ``to:…``)."""
    ends = (("from", created_from), ("to", created_to))
    created_at = [f"{end}:{value}" for end, value in ends if value is not None]
    params = {"createdBy": created_by, "createdAt": created_at or None}
    return Endpoint(HTTPMethod.GET, "worklog", ItemList[Worklog], params=params)


def create(issue_key: str, body: WorklogCreate) -> Endpoint[Worklog]:
    return Endpoint(HTTPMethod.POST, f"issues/{segment(issue_key)}/worklog", Worklog, json=body)


def update(issue_key: str, record_id: int | str, body: WorklogUpdate) -> Endpoint[Worklog]:
    path = f"issues/{segment(issue_key)}/worklog/{segment(record_id)}"
    return Endpoint(HTTPMethod.PATCH, path, Worklog, json=body)


def delete(issue_key: str, record_id: int | str) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"issues/{segment(issue_key)}/worklog/{segment(record_id)}")


def import_(issue_key: str, body: ImportWorklog) -> Endpoint[ItemList[Worklog]]:
    """The live endpoint answers with a JSON array of the created record(s)."""
    path = f"issues/{segment(issue_key)}/worklogs/_import"
    return Endpoint(HTTPMethod.POST, path, ItemList[Worklog], json=body)
