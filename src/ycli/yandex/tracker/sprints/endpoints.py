"""Tracker ``/sprints`` operations, declared once (sans-IO).

Writes on an existing sprint carry its current ``version`` as ``?version=`` (optimistic lock).

Examples:
    >>> start_sprint(4405, version=3).params
    {'version': 3}
    >>> list_sprints(3).path
    'boards/3/sprints'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.sprints.models import Sprint, SprintCreate, SprintUpdate


def list_sprints(board_id: int) -> Endpoint[ItemList[Sprint]]:
    return Endpoint("GET", f"boards/{segment(board_id)}/sprints", ItemList[Sprint])


def get_sprint(sprint_id: int) -> Endpoint[Sprint]:
    return Endpoint("GET", f"sprints/{segment(sprint_id)}", Sprint)


def create_sprint(body: SprintCreate) -> Endpoint[Sprint]:
    return Endpoint("POST", "sprints", Sprint, json=body)


def update_sprint(sprint_id: int, body: SprintUpdate, version: int | None) -> Endpoint[Sprint]:
    path = f"sprints/{segment(sprint_id)}"
    return Endpoint("PATCH", path, Sprint, json=body, params={"version": version})


def delete_sprint(sprint_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"sprints/{segment(sprint_id)}")


def start_sprint(sprint_id: int, version: int | None) -> Endpoint[Sprint]:
    path = f"sprints/{segment(sprint_id)}/_start"
    return Endpoint("POST", path, Sprint, params={"version": version})


def archive_sprint(sprint_id: int, version: int | None) -> Endpoint[Sprint]:
    path = f"sprints/{segment(sprint_id)}/_archive"
    return Endpoint("POST", path, Sprint, params={"version": version})
