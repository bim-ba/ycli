"""Tracker queue ``/macros`` operations, declared once (sans-IO).

Examples:
    >>> get_macro("TEST", 3).path
    'queues/TEST/macros/3'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroUpdate


def list_macros(queue_id: str) -> Endpoint[ItemList[Macro]]:
    return Endpoint("GET", f"queues/{segment(queue_id)}/macros", ItemList[Macro])


def get_macro(queue_id: str, macro_id: int) -> Endpoint[Macro]:
    return Endpoint("GET", f"queues/{segment(queue_id)}/macros/{segment(macro_id)}", Macro)


def create_macro(queue_id: str, body: MacroCreate) -> Endpoint[Macro]:
    return Endpoint("POST", f"queues/{segment(queue_id)}/macros", Macro, json=body)


def edit_macro(queue_id: str, macro_id: int, body: MacroUpdate) -> Endpoint[Macro]:
    path = f"queues/{segment(queue_id)}/macros/{segment(macro_id)}"
    return Endpoint("PATCH", path, Macro, json=body)


def delete_macro(queue_id: str, macro_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"queues/{segment(queue_id)}/macros/{segment(macro_id)}")
