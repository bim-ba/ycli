"""`tracker worklog` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="worklog", help="Tracker issue worklog.", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Tracker issue worklog."""


@app.command("list")
def list_(ctx: typer.Context, key: Annotated[str, typer.Argument(metavar="KEY", help="Issue key.")]) -> None:
    """List worklog entries for issue KEY."""
    print(tracker_client(ctx).worklog.list(key).model_dump_json(by_alias=True))
