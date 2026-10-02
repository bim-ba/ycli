"""Tracker queue ``/autoactions`` operations, declared once (sans-IO).

Examples:
    >>> get_run_log("DESIGN", 9, "abc").path
    'queues/DESIGN/autoactions/9/logs/abc'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.autoactions.models import (
    Autoaction,
    AutoactionLogList,
    AutoactionRunList,
)


def _autoaction_path(queue_id: str, action_id: int) -> str:
    return f"queues/{segment(queue_id)}/autoactions/{segment(action_id)}"


def get_autoaction(queue_id: str, action_id: int) -> Endpoint[Autoaction]:
    return Endpoint("GET", _autoaction_path(queue_id, action_id), Autoaction)


def create_autoaction(queue_id: str, body: dict[str, Any]) -> Endpoint[Autoaction]:
    return Endpoint("POST", f"queues/{segment(queue_id)}/autoactions", Autoaction, json=body)


def list_run_logs(queue_id: str, action_id: int) -> Endpoint[AutoactionLogList]:
    return Endpoint("GET", f"{_autoaction_path(queue_id, action_id)}/logs", AutoactionLogList)


def get_run_log(queue_id: str, action_id: int, run_id: str) -> Endpoint[AutoactionRunList]:
    path = f"{_autoaction_path(queue_id, action_id)}/logs/{segment(run_id)}"
    return Endpoint("GET", path, AutoactionRunList)
