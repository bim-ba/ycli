"""Tracker ``/components`` operations, declared once (sans-IO).

Example:
    >>> edit_component(111175, {"assignAuto": True}, version=1).path
    'components/111175'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.tracker.components.models import (
    Component,
    ComponentGroupAccess,
    ComponentList,
    ComponentUserAccess,
)


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


def list_queue_components(queue_id: str, *, fields: str | None = None) -> Endpoint[ComponentList]:
    return Endpoint(
        "GET", f"queues/{segment(queue_id)}/components", ComponentList, params={"fields": fields}
    )


def get_component(component_id: int, *, fields: str | None = None) -> Endpoint[Component]:
    return Endpoint(
        "GET", f"components/{segment(component_id)}", Component, params={"fields": fields}
    )


def delete_component(component_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"components/{segment(component_id)}")


def get_user_access(component_id: int, user_id: str) -> Endpoint[ComponentUserAccess]:
    path = f"components/{segment(component_id)}/permissions/users/{segment(user_id)}"
    return Endpoint("GET", path, ComponentUserAccess)


def get_group_access(component_id: int, group_id: int) -> Endpoint[ComponentGroupAccess]:
    path = f"components/{segment(component_id)}/permissions/groups/{segment(group_id)}"
    return Endpoint("GET", path, ComponentGroupAccess)
