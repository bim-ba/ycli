"""`tracker comments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.yandex.tracker._args import KeyArg

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
