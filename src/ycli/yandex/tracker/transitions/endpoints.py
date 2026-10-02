"""Tracker issue ``/transitions`` operations, declared once (sans-IO).

Example:
    >>> execute_transition("DE-1", "close", {}).path
    'issues/DE-1/transitions/close/_execute'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.transitions.models import TransitionList


def list_transitions(key: str) -> Endpoint[TransitionList]:
    return Endpoint("GET", f"issues/{segment(key)}/transitions", TransitionList)


def execute_transition(
    key: str, transition_id: str, body: dict[str, Any]
) -> Endpoint[TransitionList]:
    path = f"issues/{segment(key)}/transitions/{segment(transition_id)}/_execute"
    return Endpoint("POST", path, TransitionList, json=body)
