"""`tracker transitions` commands."""
from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.output import render

from ycli.yandex.tracker._clideps import parse_fields, tracker_client

app = typer.Typer(name="transitions", help="Tracker issue transitions.", no_args_is_help=True)

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key.")]


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List available transitions for issue KEY."""
    render(tracker_client(ctx).transitions.list(key))


@app.command()
def execute(
    ctx: typer.Context,
    key: KeyArg,
    transition_id: Annotated[str, typer.Argument(metavar="ID", help="Transition id (from `transitions list`).")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-F", help="Transition body field key=value (JSON-coerced; repeatable)."),
    ] = None,
) -> None:
    """Execute transition ID on issue KEY (optional body via --field)."""
    raw = tracker_client(ctx).transitions.execute(key, transition_id, body=parse_fields(field))
    print(json.dumps(raw, ensure_ascii=False))
