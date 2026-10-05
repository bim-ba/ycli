"""Tracker worklog operations, declared once (sans-IO).

Examples:
    >>> search({"createdBy": "alice"}).effect
    'read'
    >>> list_global("alice", ["from:2018-06-06", "to:2018-06-07"]).params["createdAt"]
    ['from:2018-06-06', 'to:2018-06-07']
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import RelativeIDPagination
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.worklog.models import (
    ImportWorklog,
    Worklog,
    WorklogCreate,
    WorklogSearch,
    WorklogUpdate,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

PAGE_SIZE = 100


def _record_id(record: Worklog) -> str | None:
    return str(record.id) if record.id is not None else None


def list_(issue_key: str, *, page_size: int = PAGE_SIZE) -> Paged[ItemList[Worklog], Worklog]:
    """``GET /issues/{key}/worklog``: ascending ids, each next page from ``id=<last record>``."""
    return Paged(
        Endpoint(
            "GET",
            f"issues/{segment(issue_key)}/worklog",
            ItemList[Worklog],
            params={"perPage": page_size},
        ),
        RelativeIDPagination(id_of=_record_id),
        lambda page: page.root,
    )


def search(body: WorklogSearch) -> Endpoint[ItemList[Worklog]]:
    """``POST /worklog/_search`` only reads."""
    # violation(arch-3): POST _search only reads
    return Endpoint("POST", "worklog/_search", ItemList[Worklog], json=body, effect="read")


def list_global(
    created_by: str | None, created_at: Sequence[str] | str | None
) -> Endpoint[ItemList[Worklog]]:
    """``GET /worklog``; a list ``created_at`` repeats ``createdAt`` (``from:…``, ``to:…``)."""
    params = {"createdBy": created_by, "createdAt": created_at}
    return Endpoint("GET", "worklog", ItemList[Worklog], params=params)


def create(issue_key: str, body: WorklogCreate) -> Endpoint[Worklog]:
    return Endpoint("POST", f"issues/{segment(issue_key)}/worklog", Worklog, json=body)


def update(issue_key: str, record_id: int | str, body: WorklogUpdate) -> Endpoint[Worklog]:
    path = f"issues/{segment(issue_key)}/worklog/{segment(record_id)}"
    return Endpoint("PATCH", path, Worklog, json=body)


def delete(issue_key: str, record_id: int | str) -> Endpoint[None]:
    return Endpoint("DELETE", f"issues/{segment(issue_key)}/worklog/{segment(record_id)}")


def import_(issue_key: str, body: ImportWorklog) -> Endpoint[ItemList[Worklog]]:
    """The live endpoint answers with a JSON array of the created record(s)."""
    path = f"issues/{segment(issue_key)}/worklogs/_import"
    return Endpoint("POST", path, ItemList[Worklog], json=body)
