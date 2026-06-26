"""`tracker comments` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="comments", help="Tracker issue comments.", no_args_is_help=True)

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key.")]


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List comments on issue KEY."""
    print(tracker_client(ctx).comments.list(key).model_dump_json(by_alias=True))


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
) -> None:
    """Add a comment to issue KEY."""
    print(tracker_client(ctx).comments.add(key, body={"text": text}).model_dump_json(by_alias=True))
