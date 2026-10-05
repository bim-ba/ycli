"""`tracker transitions` commands."""

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.transitions.models import Transition, TransitionExecute
from ycli.yandex.tracker.typedefs import (
    IssueKeyArg,
)

app = typer.Typer(name="transitions", help="Tracker issue transitions.", no_args_is_help=True)


@app.command("list")
def list_(issue_key: IssueKeyArg, *, tracker: TrackerClient) -> ItemList[Transition]:
    """List available transitions for issue ISSUE_KEY."""
    return tracker.transitions.list(issue_key)


@app.command()
def execute(
    issue_key: IssueKeyArg,
    transition_id: Annotated[
        str, typer.Argument(metavar="ID", help="Transition id (from `transitions list`).")
    ],
    *,
    tracker: TrackerClient,
) -> ItemList[Transition]:
    """Execute transition ID on issue ISSUE_KEY; -F gives the fields its screen asks for."""
    return tracker.transitions.execute(issue_key, transition_id, body=TransitionExecute())
