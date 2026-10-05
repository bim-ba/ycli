"""`tracker priorities` commands."""

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
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="Priority name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="Priority name in English.")
    ] = None,
    order: Annotated[int | None, typer.Option(help="Display-order weight of the priority.")] = None,
    description: Annotated[str | None, typer.Option(help="Description of the priority.")] = None,
    *,
    tracker: TrackerClient,
) -> Priority:
    """Create a priority (POST /priorities/)."""
    body = PriorityCreate(
        key=key,
        name=LocalizedName(ru=name_ru, en=name_en),
        order=order,
        description=description,
    )
    return tracker.priorities.create(body)


@app.command()
def update(
    priority_id: Annotated[str, typer.Argument(metavar="PRIORITY_ID", help="Priority id or key.")],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="New priority name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="New priority name in English.")
    ] = None,
    description: Annotated[
        str | None, typer.Option(help="New description of the priority.")
    ] = None,
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Priority:
    """Edit priority PRIORITY_ID (PATCH /priorities/{id}?version=)."""
    named = name_ru is not None or name_en is not None
    body = PriorityUpdate(
        name=LocalizedName(ru=name_ru, en=name_en) if named else None,
        description=description,
    )
    return tracker.priorities.update(priority_id, body, version=version)
