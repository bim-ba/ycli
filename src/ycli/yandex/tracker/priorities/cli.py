"""`tracker priorities` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.priorities.models import LocalizedName, PriorityCreate, PriorityUpdate

app = typer.Typer(name="priorities", help="Tracker priorities.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all priorities."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.priorities.list(), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
    key: Annotated[str, typer.Option(help="Key of the new priority.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Priority name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Priority name in English.")] = "",
    order: Annotated[int | None, typer.Option(help="Display-order weight of the priority.")] = None,
    description: Annotated[str, typer.Option(help="Description of the priority.")] = "",
) -> None:
    """Create a priority (POST /priorities/)."""
    body = PriorityCreate(
        key=key,
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
        order=order,
        description=description or None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.priorities.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def edit(
    ctx: typer.Context,
    priority_id: Annotated[str, typer.Argument(metavar="PRIORITY_ID", help="Priority id or key.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New priority name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New priority name in English.")] = "",
    description: Annotated[str, typer.Option(help="New description of the priority.")] = "",
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
) -> None:
    """Edit priority PRIORITY_ID (PATCH /priorities/{id}?version=)."""
    named = bool(name_ru or name_en)
    body = PriorityUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        description=description or None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.priorities.edit(priority_id, body, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )
