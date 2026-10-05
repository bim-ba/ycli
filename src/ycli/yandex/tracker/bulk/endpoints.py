"""Tracker ``/bulkchange`` operations, each declared once (sans-IO).

The two reads poll an operation that ``issues.update_bulk``, ``move_bulk`` or
``transition_bulk`` started.

Examples:
    >>> get("1ab2").path
    'bulkchange/1ab2'
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.bulk.models import BulkChange, BulkIssueResult


def get(bulk_id: str) -> Endpoint[BulkChange]:
    return Endpoint(HTTPMethod.GET, f"bulkchange/{segment(bulk_id)}", BulkChange)


def issues_list(bulk_id: str) -> Endpoint[ItemList[BulkIssueResult]]:
    return Endpoint(
        HTTPMethod.GET, f"bulkchange/{segment(bulk_id)}/issues", ItemList[BulkIssueResult]
    )
