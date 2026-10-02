"""Tracker ``/components`` operations, declared once (sans-IO).

Example:
    >>> edit_component(111175, {"assignAuto": True}, version=1).path
    'components/111175'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.components.models import Component, ComponentList


def list_components() -> Endpoint[ComponentList]:
    return Endpoint("GET", "components", ComponentList)


def create_component(body: dict[str, Any]) -> Endpoint[Component]:
    return Endpoint("POST", "components", Component, json=body)


def edit_component(
    component_id: int, body: dict[str, Any], *, version: int | None = None
) -> Endpoint[Component]:
    """``PATCH /components/{id}?version=`` — ``version`` is the optimistic lock, sent when set."""
    return Endpoint(
        "PATCH",
        f"components/{segment(component_id)}",
        Component,
        json=body,
        params={"version": version},
    )
