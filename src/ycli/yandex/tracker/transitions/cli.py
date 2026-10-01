"""`tracker transitions` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.fields import parse_fields
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.transitions.models import TransitionList
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)

app = typer.Typer(name="transitions", help="Tracker issue transitions.", no_args_is_help=True)


@app.command("list")
def list_(key: KeyArg, *, tracker: TrackerClient) -> TransitionList:
    """List available transitions for issue KEY."""
    return tracker.transitions.list(key)


@app.command()
def execute(
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
    *,
    tracker: TrackerClient,
) -> TransitionList:
    """Execute transition ID on issue KEY (optional body via --field)."""
    return tracker.transitions.execute(key, transition_id, body=parse_fields(field))
