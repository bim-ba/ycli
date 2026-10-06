"""Tracker issue ``/checklistItems`` operations, declared once (sans-IO).

The read returns a bare array of items; every write — the deletes included, which the API
answers with ``200`` and a body — returns the issue with its updated checklist.

Examples:
    >>> clear("DE-1").effect
    <Effect.DESTRUCTIVE: 'destructive'>
    >>> update("DE-1", "5f", {"checked": True}).path
    'issues/DE-1/checklistItems/5f'
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.checklists.models import (
    ChecklistItem,
    ChecklistItemCreate,
    ChecklistItemUpdate,
)
from ycli.yandex.tracker.models import Issue


def list_(issue_key: str) -> Endpoint[ItemList[ChecklistItem]]:
    return Endpoint(
        HTTPMethod.GET, f"issues/{segment(issue_key)}/checklistItems", ItemList[ChecklistItem]
    )


def create(issue_key: str, body: ChecklistItemCreate) -> Endpoint[Issue]:
    return Endpoint(
        HTTPMethod.POST, f"issues/{segment(issue_key)}/checklistItems", Issue, json=body
    )


def update(issue_key: str, item_id: str, body: ChecklistItemUpdate) -> Endpoint[Issue]:
    path = f"issues/{segment(issue_key)}/checklistItems/{segment(item_id)}"
    return Endpoint(HTTPMethod.PATCH, path, Issue, json=body)


def delete(issue_key: str, item_id: str) -> Endpoint[Issue]:
    path = f"issues/{segment(issue_key)}/checklistItems/{segment(item_id)}"
    return Endpoint(HTTPMethod.DELETE, path, Issue)


def clear(issue_key: str) -> Endpoint[Issue]:
    return Endpoint(HTTPMethod.DELETE, f"issues/{segment(issue_key)}/checklistItems", Issue)
