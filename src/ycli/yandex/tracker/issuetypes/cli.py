"""`tracker issuetypes` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.issuetypes.models import (
    IssueTypeCreate,
    IssueTypeUpdate,
    LocalizedName,
)

app = typer.Typer(name="issuetypes", help="Tracker issue types.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all issue types."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.issuetypes.list(), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
    key: Annotated[str, typer.Option(help="Key of the new issue type.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Issue type name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Issue type name in English.")] = "",
) -> None:
    """Create an issue type (POST /issuetypes/)."""
    body = IssueTypeCreate(
        key=key,
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.issuetypes.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def edit(
    ctx: typer.Context,
    issue_type_id: Annotated[
        str, typer.Argument(metavar="ISSUE_TYPE_ID", help="Issue type id or key.")
    ],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New issue type name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New issue type name in English.")] = "",
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
) -> None:
    """Edit issue type ISSUE_TYPE_ID (PATCH /issuetypes/{id}?version=)."""
    body = IssueTypeUpdate(name=LocalizedName(ru=name_ru or None, en=name_en or None))
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.issuetypes.edit(issue_type_id, body, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )
