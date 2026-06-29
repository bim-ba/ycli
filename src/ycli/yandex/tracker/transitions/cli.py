"""`tracker transitions` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker._types import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)
from ycli.yandex.tracker._utils import parse_fields

app = typer.Typer(name="transitions", help="Tracker issue transitions.", no_args_is_help=True)


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List available transitions for issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.transitions.list(key), app_ctx.strategy, app_ctx.console)


@app.command()
def execute(
    ctx: typer.Context,
    key: KeyArg,
    transition_id: Annotated[
        str, typer.Argument(metavar="ID", help="Transition id (from `transitions list`).")
    ],
    field: Annotated[
        list[str] | None,
        typer.Option(
            "--field", "-F", help="Transition body field key=value (JSON-coerced; repeatable)."
        ),
    ] = None,
) -> None:
    """Execute transition ID on issue KEY (optional body via --field)."""
    app_ctx = AppContext.from_typer_context(ctx)
    result = app_ctx.tracker.transitions.execute(key, transition_id, body=parse_fields(field))
    Serializer.serialize(result, app_ctx.strategy, app_ctx.console)
