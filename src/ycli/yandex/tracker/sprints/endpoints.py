"""Tracker ``/sprints`` operations, declared once (sans-IO).

Writes on an existing sprint carry its current ``version`` as ``?version=`` (optimistic lock).

Examples:
    >>> start(4405, version=3).params
    {'version': 3}
    >>> list_(3).path
    'boards/3/sprints'
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.sprints.models import Sprint, SprintCreate, SprintUpdate


def list_(board_id: int) -> Endpoint[ItemList[Sprint]]:
    return Endpoint(HTTPMethod.GET, f"boards/{segment(board_id)}/sprints", ItemList[Sprint])


def get(sprint_id: int) -> Endpoint[Sprint]:
    return Endpoint(HTTPMethod.GET, f"sprints/{segment(sprint_id)}", Sprint)


def create(body: SprintCreate) -> Endpoint[Sprint]:
    return Endpoint(HTTPMethod.POST, "sprints", Sprint, json=body)


def update(sprint_id: int, body: SprintUpdate, version: int | None) -> Endpoint[Sprint]:
    path = f"sprints/{segment(sprint_id)}"
    return Endpoint(HTTPMethod.PATCH, path, Sprint, json=body, params={"version": version})


def delete(sprint_id: int) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"sprints/{segment(sprint_id)}")


def start(sprint_id: int, version: int | None) -> Endpoint[Sprint]:
    path = f"sprints/{segment(sprint_id)}/_start"
    return Endpoint(HTTPMethod.POST, path, Sprint, params={"version": version})


def archive(sprint_id: int, version: int | None) -> Endpoint[Sprint]:
    path = f"sprints/{segment(sprint_id)}/_archive"
    return Endpoint(HTTPMethod.POST, path, Sprint, params={"version": version})
