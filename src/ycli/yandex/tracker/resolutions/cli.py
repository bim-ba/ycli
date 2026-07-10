"""`tracker resolutions` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.resolutions.models import (
    LocalizedName,
    ResolutionCreate,
    ResolutionUpdate,
)

app = typer.Typer(name="resolutions", help="Tracker issue resolutions.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all issue resolutions."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.resolutions.list(), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
    key: Annotated[str, typer.Option(help="Key of the new resolution (Latin, lower-case start).")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Resolution name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Resolution name in English.")] = "",
) -> None:
    """Create an issue resolution (POST /resolutions/)."""
    body = ResolutionCreate(
        key=key,
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.resolutions.create(body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
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
) -> None:
    """Edit issue resolution RESOLUTION_ID (PATCH /resolutions/{id}?version=)."""
    named = bool(name_ru or name_en)
    body = ResolutionUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        description=description or None,
        order=order,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.resolutions.edit(resolution_id, body, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )
