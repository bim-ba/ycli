"""Tracker queue ``/macros`` operations, declared once (sans-IO).

Examples:
    >>> get_macro("TEST", 3).path
    'queues/TEST/macros/3'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.macros.models import Macro, MacroList


def list_macros(queue_id: str) -> Endpoint[MacroList]:
    return Endpoint("GET", f"queues/{segment(queue_id)}/macros", MacroList)


def get_macro(queue_id: str, macro_id: int) -> Endpoint[Macro]:
    return Endpoint("GET", f"queues/{segment(queue_id)}/macros/{segment(macro_id)}", Macro)


def create_macro(queue_id: str, body: dict[str, Any]) -> Endpoint[Macro]:
    return Endpoint("POST", f"queues/{segment(queue_id)}/macros", Macro, json=body)


def edit_macro(queue_id: str, macro_id: int, body: dict[str, Any]) -> Endpoint[Macro]:
    path = f"queues/{segment(queue_id)}/macros/{segment(macro_id)}"
    return Endpoint("PATCH", path, Macro, json=body)


def delete_macro(queue_id: str, macro_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"queues/{segment(queue_id)}/macros/{segment(macro_id)}")
