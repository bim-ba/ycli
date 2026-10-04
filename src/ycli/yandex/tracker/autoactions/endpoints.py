"""Tracker queue ``/autoactions`` operations, declared once (sans-IO).

Examples:
    >>> logs_get("DESIGN", 9, "abc").path
    'queues/DESIGN/autoactions/9/logs/abc'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.autoactions.models import (
    Autoaction,
    AutoactionCreate,
    AutoactionLogEntry,
    AutoactionRunEntry,
)


def _autoaction_path(queue_id: str, action_id: int) -> str:
    return f"queues/{segment(queue_id)}/autoactions/{segment(action_id)}"


def get(queue_id: str, action_id: int) -> Endpoint[Autoaction]:
    return Endpoint("GET", _autoaction_path(queue_id, action_id), Autoaction)


def create(queue_id: str, body: AutoactionCreate) -> Endpoint[Autoaction]:
    return Endpoint("POST", f"queues/{segment(queue_id)}/autoactions", Autoaction, json=body)


def logs_list(queue_id: str, action_id: int) -> Endpoint[ItemList[AutoactionLogEntry]]:
    return Endpoint(
        "GET", f"{_autoaction_path(queue_id, action_id)}/logs", ItemList[AutoactionLogEntry]
    )


def logs_get(queue_id: str, action_id: int, run_id: str) -> Endpoint[ItemList[AutoactionRunEntry]]:
    path = f"{_autoaction_path(queue_id, action_id)}/logs/{segment(run_id)}"
    return Endpoint("GET", path, ItemList[AutoactionRunEntry])
