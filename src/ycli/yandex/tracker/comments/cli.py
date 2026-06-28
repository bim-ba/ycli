"""`tracker comments` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.cliformat import output_format
from ycli.output import render

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="comments", help="Tracker issue comments.", no_args_is_help=True)

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key.")]


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List comments on issue KEY."""
    render(tracker_client(ctx).comments.list(key), output_format=output_format(ctx))


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
) -> None:
    """Add a comment to issue KEY."""
    render(tracker_client(ctx).comments.add(key, body={"text": text}), output_format=output_format(ctx))
