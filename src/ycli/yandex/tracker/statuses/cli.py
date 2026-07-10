"""`tracker statuses` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.statuses.models import LocalizedName, StatusCreate, StatusUpdate

app = typer.Typer(name="statuses", help="Tracker issue statuses.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all issue statuses."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.statuses.list(), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
    key: Annotated[str, typer.Option(help="Key of the new status (Latin, lower-case start).")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Status name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Status name in English.")] = "",
    type_: Annotated[
        str, typer.Option("--type", help="Status type: new/inProgress/paused/done/cancelled.")
    ] = "new",
) -> None:
    """Create an issue status (POST /statuses/)."""
    body = StatusCreate(
        key=key,
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
        type=type_,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.statuses.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def edit(
    ctx: typer.Context,
    status_id: Annotated[str, typer.Argument(metavar="STATUS_ID", help="Status id or key.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New status name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New status name in English.")] = "",
    description: Annotated[str, typer.Option(help="New status description.")] = "",
    type_: Annotated[str, typer.Option("--type", help="New status type.")] = "",
    order: Annotated[int | None, typer.Option(help="New display-order weight.")] = None,
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
) -> None:
    """Edit issue status STATUS_ID (PATCH /statuses/{id}?version=)."""
    named = bool(name_ru or name_en)
    body = StatusUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        description=description or None,
        type=type_ or None,
        order=order,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.statuses.edit(status_id, body, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )
