"""Tracker issue ``/checklistItems`` operations, declared once (sans-IO).

The read returns a bare array of items; every write — the deletes included, which the API
answers with ``200`` and a body — returns the issue with its updated checklist.

Examples:
    >>> clear("DE-1").effect
    'destructive'
    >>> update("DE-1", "5f", {"checked": True}).path
    'issues/DE-1/checklistItems/5f'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.checklists.models import (
    Checklist,
    ChecklistItem,
    ChecklistItemCreate,
    ChecklistItemUpdate,
)


def list_(issue_key: str) -> Endpoint[ItemList[ChecklistItem]]:
    return Endpoint("GET", f"issues/{segment(issue_key)}/checklistItems", ItemList[ChecklistItem])


def create(issue_key: str, body: ChecklistItemCreate) -> Endpoint[Checklist]:
    return Endpoint("POST", f"issues/{segment(issue_key)}/checklistItems", Checklist, json=body)


def update(issue_key: str, item_id: str, body: ChecklistItemUpdate) -> Endpoint[Checklist]:
    path = f"issues/{segment(issue_key)}/checklistItems/{segment(item_id)}"
    return Endpoint("PATCH", path, Checklist, json=body)


def delete(issue_key: str, item_id: str) -> Endpoint[Checklist]:
    path = f"issues/{segment(issue_key)}/checklistItems/{segment(item_id)}"
    return Endpoint("DELETE", path, Checklist)


def clear(issue_key: str) -> Endpoint[Checklist]:
    return Endpoint("DELETE", f"issues/{segment(issue_key)}/checklistItems", Checklist)
