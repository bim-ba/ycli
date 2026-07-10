"""`forms operations` commands (reads only)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="operations", help="Forms async operations.", no_args_is_help=True)

OperationIdArg = Annotated[
    str,
    typer.Argument(
        metavar="OPERATION_ID", help="Operation id from an async trigger (e.g. answers export)."
    ),
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(ctx: typer.Context, operation_id: OperationIdArg) -> None:
    """Print the status of async operation OPERATION_ID (GET /operations/{id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.operations.get(operation_id), app_ctx.strategy, app_ctx.console
    )
