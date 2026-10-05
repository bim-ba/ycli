"""`wiki operations` commands — read the status of an async page/grid clone."""

from typing import Annotated

import typer

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.operations.models import (
    CloneOperationStatus,
    GridCloneOperationStatus,
    MoveOperationStatus,
)

app = typer.Typer(
    name="operations",
    help="Wiki async operation status (clone and move polling).",
    no_args_is_help=True,
)

TaskIDArg = Annotated[
    str, typer.Argument(metavar="TASK_ID", help="Operation task id (from a clone or move trigger).")
]


@app.command()
def clone_get(task_id: TaskIDArg, *, wiki: WikiClient) -> CloneOperationStatus:
    """Print a page-clone operation's status (GET /operations/clone/{task_id})."""
    return wiki.operations.clone_get(task_id)


@app.command()
def clone_inline_grid_get(task_id: TaskIDArg, *, wiki: WikiClient) -> GridCloneOperationStatus:
    """Print a grid-clone operation's status (GET /operations/clone_inline_grid/{task_id})."""
    return wiki.operations.clone_inline_grid_get(task_id)


@app.command("move-get")
def move_get(task_id: TaskIDArg, *, wiki: WikiClient) -> MoveOperationStatus:
    """Print a page-move operation's status (GET /operations/move/{task_id}); undocumented API."""
    return wiki.operations.move_get(task_id)
