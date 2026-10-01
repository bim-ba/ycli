"""`wiki operations` commands — read the status of an async page/grid clone."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.operations.models import CloneOperationStatus, GridCloneOperationStatus

app = typer.Typer(
    name="operations", help="Wiki async operation status (clone polling).", no_args_is_help=True
)

TaskIdArg = Annotated[
    str, typer.Argument(metavar="TASK_ID", help="Operation task id (from a clone trigger).")
]


@app.command()
def clone(task_id: TaskIdArg, *, wiki: WikiClient) -> CloneOperationStatus:
    """Print a page-clone operation's status (GET /operations/clone/{task_id})."""
    return wiki.operations.clone_get(task_id)


@app.command()
def gridclone(task_id: TaskIdArg, *, wiki: WikiClient) -> GridCloneOperationStatus:
    """Print a grid-clone operation's status (GET /operations/clone_inline_grid/{task_id})."""
    return wiki.operations.gridclone_get(task_id)
