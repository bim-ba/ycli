"""`tracker components` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.components.models import ComponentCreate, ComponentUpdate

app = typer.Typer(name="components", help="Tracker components.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all components created in the organisation."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.components.list(), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Display name of the new component.")],
    queue: Annotated[str, typer.Option(help="Key of the queue the component is created in.")],
    description: Annotated[str, typer.Option(help="Text description of the component.")] = "",
    lead: Annotated[str, typer.Option(help="Login of the component's owner (lead).")] = "",
    assign_auto: Annotated[
        bool | None,
        typer.Option("--assign-auto/--no-assign-auto", help="Auto-assign the owner to issues."),
    ] = None,
) -> None:
    """Create a component (POST /components)."""
    body = ComponentCreate(
        name=name,
        queue=queue,
        description=description or None,
        lead=lead or None,
        assign_auto=assign_auto,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.components.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def edit(
    ctx: typer.Context,
    component_id: Annotated[
        int, typer.Argument(metavar="COMPONENT_ID", help="Numeric id of the component.")
    ],
    name: Annotated[str, typer.Option(help="New display name of the component.")] = "",
    description: Annotated[str, typer.Option(help="New text description of the component.")] = "",
    lead: Annotated[str, typer.Option(help="New login of the component's owner (lead).")] = "",
    assign_auto: Annotated[
        bool | None,
        typer.Option("--assign-auto/--no-assign-auto", help="Auto-assign the owner to issues."),
    ] = None,
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
) -> None:
    """Edit component COMPONENT_ID (PATCH /components/{id}?version=)."""
    body = ComponentUpdate(
        name=name or None,
        description=description or None,
        lead=lead or None,
        assign_auto=assign_auto,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.components.edit(component_id, body, version=version),
        app_ctx.strategy,
        app_ctx.console,
    )
