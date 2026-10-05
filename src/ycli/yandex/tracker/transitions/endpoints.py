"""Tracker issue ``/transitions`` operations, declared once (sans-IO).

Examples:
    >>> execute("DE-1", "close", {}).path
    'issues/DE-1/transitions/close/_execute'
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.transitions.models import Transition, TransitionExecute


def list_(issue_key: str) -> Endpoint[ItemList[Transition]]:
    return Endpoint(
        HTTPMethod.GET, f"issues/{segment(issue_key)}/transitions", ItemList[Transition]
    )


def execute(
    issue_key: str, transition_id: str, body: TransitionExecute
) -> Endpoint[ItemList[Transition]]:
    path = f"issues/{segment(issue_key)}/transitions/{segment(transition_id)}/_execute"
    return Endpoint(HTTPMethod.POST, path, ItemList[Transition], json=body)
