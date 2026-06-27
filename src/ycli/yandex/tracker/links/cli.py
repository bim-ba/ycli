"""`tracker links` commands."""
from __future__ import annotations

from enum import Enum
from typing import Annotated

import typer

from ycli.output import render

from ycli.yandex.tracker._clideps import tracker_client

app = typer.Typer(name="links", help="Tracker issue links.", no_args_is_help=True)

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key.")]


class Relationship(str, Enum):
    """Link relationship verbs accepted by ``POST /issues/{key}/links``."""

    DEPENDS_ON = "depends on"
    IS_DEPENDENT_BY = "is dependent by"
    RELATES = "relates"
    DUPLICATES = "duplicates"
    IS_DUPLICATED_BY = "is duplicated by"
    SUBTASK = "subtask"
    PARENT = "parent"


@app.command("list")
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List links for issue KEY."""
    render(tracker_client(ctx).links.list(key))


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    relationship: Annotated[Relationship, typer.Argument(help="Relationship verb.")],
    target: Annotated[str, typer.Argument(help="Target issue key, e.g. DATAENGINEERING-2.")],
) -> None:
    """Link issue KEY to TARGET with RELATIONSHIP."""
    body = {"relationship": relationship.value, "issue": target}
    render(tracker_client(ctx).links.add(key, body=body))
