"""`tracker components` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.components.models import (
    Component,
    ComponentCreate,
    ComponentList,
    ComponentUpdate,
)

app = typer.Typer(name="components", help="Tracker components.", no_args_is_help=True)


@app.command("list")
def list_(*, tracker: TrackerClient) -> ComponentList:
    """List all components created in the organisation."""
    return tracker.components.list()


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Display name of the new component.")],
    queue: Annotated[str, typer.Option(help="Key of the queue the component is created in.")],
    description: Annotated[str, typer.Option(help="Text description of the component.")] = "",
    lead: Annotated[str, typer.Option(help="Login of the component's owner (lead).")] = "",
    assign_auto: Annotated[
        bool | None,
        typer.Option("--assign-auto/--no-assign-auto", help="Auto-assign the owner to issues."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Component:
    """Create a component (POST /components)."""
    body = ComponentCreate(
        name=name,
        queue=queue,
        description=description or None,
        lead=lead or None,
        assign_auto=assign_auto,
    )
    return tracker.components.create(body)


@app.command()
def edit(
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
    *,
    tracker: TrackerClient,
) -> Component:
    """Edit component COMPONENT_ID (PATCH /components/{id}?version=)."""
    body = ComponentUpdate(
        name=name or None,
        description=description or None,
        lead=lead or None,
        assign_auto=assign_auto,
    )
    return tracker.components.edit(component_id, body, version=version)
