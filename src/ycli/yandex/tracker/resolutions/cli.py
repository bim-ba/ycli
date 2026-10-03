"""`tracker resolutions` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.aliases import deprecated_alias
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.resolutions.models import (
    Resolution,
    ResolutionCreate,
    ResolutionList,
    ResolutionUpdate,
)

app = typer.Typer(name="resolutions", help="Tracker issue resolutions.", no_args_is_help=True)


@app.command("list")
def list_(*, tracker: TrackerClient) -> ResolutionList:
    """List all issue resolutions."""
    return tracker.resolutions.list()


@app.command()
def create(
    key: Annotated[str, typer.Option(help="Key of the new resolution (Latin, lower-case start).")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Resolution name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Resolution name in English.")] = "",
    *,
    tracker: TrackerClient,
) -> Resolution:
    """Create an issue resolution (POST /resolutions/)."""
    body = ResolutionCreate(
        key=key,
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
    )
    return tracker.resolutions.create(body)


@deprecated_alias(app, "edit")
@app.command()
def update(
    resolution_id: Annotated[
        str, typer.Argument(metavar="RESOLUTION_ID", help="Resolution id or key.")
    ],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New resolution name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New resolution name in English.")] = "",
    description: Annotated[str, typer.Option(help="New resolution description.")] = "",
    order: Annotated[int | None, typer.Option(help="New display-order weight.")] = None,
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Resolution:
    """Edit issue resolution RESOLUTION_ID (PATCH /resolutions/{id}?version=)."""
    named = bool(name_ru or name_en)
    body = ResolutionUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        description=description or None,
        order=order,
    )
    return tracker.resolutions.edit(resolution_id, body, version=version)
