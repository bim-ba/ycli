"""Tracker issue ``/transitions`` operations, declared once (sans-IO).

Examples:
    >>> execute_transition("DE-1", "close", {}).path
    'issues/DE-1/transitions/close/_execute'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.transitions.models import Transition


def list_transitions(key: str) -> Endpoint[ItemList[Transition]]:
    return Endpoint("GET", f"issues/{segment(key)}/transitions", ItemList[Transition])


def execute_transition(
    key: str, transition_id: str, body: dict[str, Any]
) -> Endpoint[ItemList[Transition]]:
    path = f"issues/{segment(key)}/transitions/{segment(transition_id)}/_execute"
    return Endpoint("POST", path, ItemList[Transition], json=body)
