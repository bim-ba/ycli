"""`tracker comments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker._types import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="comments", help="Tracker issue comments.", no_args_is_help=True)


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List comments on issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.comments.list(key), app_ctx.strategy, app_ctx.console)


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
) -> None:
    """Add a comment to issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.comments.add(key, body={"text": text}), app_ctx.strategy, app_ctx.console
    )
