"""Wiki ``/operations`` status reads, declared once (sans-IO).

Example:
    >>> get_clone_status("task-1").path
    'operations/clone/task-1'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.wiki.operations.models import (
    CloneOperationStatus,
    GridCloneOperationStatus,
    MoveOperationStatus,
)


def get_clone_status(task_id: str) -> Endpoint[CloneOperationStatus]:
    return Endpoint("GET", f"operations/clone/{segment(task_id)}", CloneOperationStatus)


def get_grid_clone_status(task_id: str) -> Endpoint[GridCloneOperationStatus]:
    path = f"operations/clone_inline_grid/{segment(task_id)}"
    return Endpoint("GET", path, GridCloneOperationStatus)


def get_move_status(task_id: str) -> Endpoint[MoveOperationStatus]:
    return Endpoint("GET", f"operations/move/{segment(task_id)}", MoveOperationStatus)
