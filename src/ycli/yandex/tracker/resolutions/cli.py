"""`tracker resolutions` commands."""

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.resolutions.models import Resolution, ResolutionCreate, ResolutionUpdate

app = typer.Typer(name="resolutions", help="Tracker issue resolutions.", no_args_is_help=True)


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[Resolution]:
    """List all issue resolutions."""
    return tracker.resolutions.list()


@app.command()
def create(
    key: Annotated[str, typer.Option(help="Key of the new resolution (Latin, lower-case start).")],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="Resolution name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="Resolution name in English.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Resolution:
    """Create an issue resolution (POST /resolutions/)."""
    body = ResolutionCreate(
        key=key,
        name=LocalizedName(ru=name_ru, en=name_en),
    )
    return tracker.resolutions.create(body)


@app.command()
def update(
    resolution_id: Annotated[
        str, typer.Argument(metavar="RESOLUTION_ID", help="Resolution id or key.")
    ],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="New resolution name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="New resolution name in English.")
    ] = None,
    description: Annotated[str | None, typer.Option(help="New resolution description.")] = None,
    order: Annotated[int | None, typer.Option(help="New display-order weight.")] = None,
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Resolution:
    """Edit issue resolution RESOLUTION_ID (PATCH /resolutions/{id}?version=)."""
    named = name_ru is not None or name_en is not None
    body = ResolutionUpdate(
        name=LocalizedName(ru=name_ru, en=name_en) if named else None,
        description=description,
        order=order,
    )
    return tracker.resolutions.update(resolution_id, body, version=version)
