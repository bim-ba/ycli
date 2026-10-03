"""Tracker ``/bulkchange`` operations, each declared once (sans-IO).

Every trigger starts a new async operation, so even ``_update`` is a plain (non-idempotent)
write; the two reads poll it.

Examples:
    >>> update_bulk({"issues": ["TEST-1"]}, notify=None).effect
    'write'
    >>> get_bulk("1ab2").path
    'bulkchange/1ab2'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.bulk.models import (
    BulkChange,
    BulkIssueResult,
    BulkMove,
    BulkTransition,
    BulkUpdate,
)


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


def get_bulk(bulk_id: str) -> Endpoint[BulkChange]:
    return Endpoint("GET", f"bulkchange/{segment(bulk_id)}", BulkChange)


def list_bulk_issues(bulk_id: str) -> Endpoint[ItemList[BulkIssueResult]]:
    return Endpoint("GET", f"bulkchange/{segment(bulk_id)}/issues", ItemList[BulkIssueResult])
