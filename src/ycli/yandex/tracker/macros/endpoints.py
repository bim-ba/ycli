"""Tracker queue ``/macros`` operations, declared once (sans-IO).

Examples:
    >>> get("TEST", 3).path
    'queues/TEST/macros/3'
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.macros.models import Macro, MacroCreate, MacroUpdate


def list_(queue_id: str) -> Endpoint[ItemList[Macro]]:
    return Endpoint(HTTPMethod.GET, f"queues/{segment(queue_id)}/macros", ItemList[Macro])


def get(queue_id: str, macro_id: int) -> Endpoint[Macro]:
    return Endpoint(HTTPMethod.GET, f"queues/{segment(queue_id)}/macros/{segment(macro_id)}", Macro)


def create(queue_id: str, body: MacroCreate) -> Endpoint[Macro]:
    return Endpoint(HTTPMethod.POST, f"queues/{segment(queue_id)}/macros", Macro, json=body)


def update(queue_id: str, macro_id: int, body: MacroUpdate) -> Endpoint[Macro]:
    path = f"queues/{segment(queue_id)}/macros/{segment(macro_id)}"
    return Endpoint(HTTPMethod.PATCH, path, Macro, json=body)


def delete(queue_id: str, macro_id: int) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"queues/{segment(queue_id)}/macros/{segment(macro_id)}")
