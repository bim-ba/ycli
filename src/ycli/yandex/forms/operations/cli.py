"""`forms operations` commands (reads only)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.models import OperationResult

app = typer.Typer(name="operations", help="Forms async operations.", no_args_is_help=True)

OperationIDArg = Annotated[
    str,
    typer.Argument(
        metavar="OPERATION_ID", help="Operation id from an async trigger (e.g. answers export)."
    ),
]


@app.command()
def get(operation_id: OperationIDArg, *, forms: FormsClient) -> OperationResult:
    """Print the status of async operation OPERATION_ID (GET /operations/{id})."""
    return forms.operations.get(operation_id)
