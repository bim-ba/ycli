"""`tracker components` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.aliases import deprecated_alias
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.components.models import (
    Component,
    ComponentCreate,
    ComponentGroupAccess,
    ComponentUpdate,
    ComponentUserAccess,
)

app = typer.Typer(name="components", help="Tracker components.", no_args_is_help=True)

ComponentIdArg = Annotated[
    int, typer.Argument(metavar="COMPONENT_ID", help="Numeric id of the component.")
]
FieldsOpt = Annotated[
    str, typer.Option(help="Comma-separated fields to return, e.g. name,description,lead.")
]


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[Component]:
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


@deprecated_alias(app, "edit")
@app.command()
def update(
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


@app.command("list-for-queue")
def list_for_queue(
    queue_id: Annotated[
        str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
    ],
    fields: FieldsOpt = "",
    *,
    tracker: TrackerClient,
) -> ItemList[Component]:
    """List the components of one queue (GET /queues/{id}/components)."""
    return tracker.components.list_for_queue(queue_id, fields=fields or None)


@app.command()
def get(
    component_id: ComponentIdArg, fields: FieldsOpt = "", *, tracker: TrackerClient
) -> Component:
    """Print component COMPONENT_ID (GET /components/{id})."""
    return tracker.components.get(component_id, fields=fields or None)


@app.command()
def delete(component_id: ComponentIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete component COMPONENT_ID (DELETE /components/{id})."""
    tracker.components.delete(component_id)
    return Ack.deleted("component", component_id)


@deprecated_alias(app, "user-permissions")
@app.command("user-permissions-get")
def user_permissions_get(
    component_id: ComponentIdArg,
    user_id: Annotated[
        str, typer.Argument(metavar="USER", help="Login or numeric uid of the user.")
    ],
    *,
    tracker: TrackerClient,
) -> ComponentUserAccess:
    """Show what USER may do on a component (GET /components/{id}/permissions/users/{user})."""
    return tracker.components.user_permissions(component_id, user_id)


@deprecated_alias(app, "group-permissions")
@app.command("group-permissions-get")
def group_permissions_get(
    component_id: ComponentIdArg,
    group_id: Annotated[int, typer.Argument(metavar="GROUP_ID", help="Numeric id of the group.")],
    *,
    tracker: TrackerClient,
) -> ComponentGroupAccess:
    """Show what GROUP_ID may do on a component (…/permissions/groups/{group})."""
    return tracker.components.group_permissions(component_id, group_id)
