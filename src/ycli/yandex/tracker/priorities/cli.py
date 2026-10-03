"""`tracker priorities` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.priorities.models import Priority, PriorityCreate, PriorityUpdate

app = typer.Typer(name="priorities", help="Tracker priorities.", no_args_is_help=True)


@app.command("list")
def list_(
    localized: Annotated[
        bool | None,
        typer.Option(
            "--localized/--no-localized", help="--no-localized returns the names in every language."
        ),
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Priority]:
    """List all priorities."""
    return tracker.priorities.list(localized=localized)


@app.command()
def create(
    key: Annotated[str, typer.Option(help="Key of the new priority.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Priority name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Priority name in English.")] = "",
    order: Annotated[int | None, typer.Option(help="Display-order weight of the priority.")] = None,
    description: Annotated[str, typer.Option(help="Description of the priority.")] = "",
    *,
    tracker: TrackerClient,
) -> Priority:
    """Create a priority (POST /priorities/)."""
    body = PriorityCreate(
        key=key,
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
        order=order,
        description=description or None,
    )
    return tracker.priorities.create(body)


@app.command()
def update(
    priority_id: Annotated[str, typer.Argument(metavar="PRIORITY_ID", help="Priority id or key.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New priority name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New priority name in English.")] = "",
    description: Annotated[str, typer.Option(help="New description of the priority.")] = "",
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Priority:
    """Edit priority PRIORITY_ID (PATCH /priorities/{id}?version=)."""
    named = bool(name_ru or name_en)
    body = PriorityUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        description=description or None,
    )
    return tracker.priorities.update(priority_id, body, version=version)
