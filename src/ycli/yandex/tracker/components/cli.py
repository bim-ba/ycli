"""`tracker components` commands."""

from typing import Annotated

import typer

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

ComponentIDArg = Annotated[
    int, typer.Argument(metavar="COMPONENT_ID", help="Numeric id of the component.")
]
ComponentFieldsOpt = Annotated[
    str | None, typer.Option(help="Comma-separated fields to return, e.g. name,description,lead.")
]


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[Component]:
    """List all components created in the organisation."""
    return tracker.components.list()


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Display name of the new component.")],
    queue: Annotated[str, typer.Option(help="Key of the queue the component is created in.")],
    description: Annotated[
        str | None, typer.Option(help="Text description of the component.")
    ] = None,
    lead: Annotated[str | None, typer.Option(help="Login of the component's owner (lead).")] = None,
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
        description=description,
        lead=lead,
        assign_auto=assign_auto,
    )
    return tracker.components.create(body)


@app.command()
def update(
    component_id: Annotated[
        int, typer.Argument(metavar="COMPONENT_ID", help="Numeric id of the component.")
    ],
    name: Annotated[str | None, typer.Option(help="New display name of the component.")] = None,
    description: Annotated[
        str | None, typer.Option(help="New text description of the component.")
    ] = None,
    lead: Annotated[
        str | None, typer.Option(help="New login of the component's owner (lead).")
    ] = None,
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
        name=name,
        description=description,
        lead=lead,
        assign_auto=assign_auto,
    )
    return tracker.components.update(component_id, body, version=version)


@app.command("list-for-queue")
def list_for_queue(
    queue_id: Annotated[
        str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
    ],
    fields: ComponentFieldsOpt = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Component]:
    """List the components of one queue (GET /queues/{id}/components)."""
    return tracker.components.list_for_queue(queue_id, fields=fields)


@app.command()
def get(
    component_id: ComponentIDArg, fields: ComponentFieldsOpt = None, *, tracker: TrackerClient
) -> Component:
    """Print component COMPONENT_ID (GET /components/{id})."""
    return tracker.components.get(component_id, fields=fields)


@app.command()
def delete(component_id: ComponentIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete component COMPONENT_ID (DELETE /components/{id})."""
    tracker.components.delete(component_id)
    return Ack.deleted("component", component_id)


@app.command("user-permissions-get")
def user_permissions_get(
    component_id: ComponentIDArg,
    user_id: Annotated[
        str, typer.Argument(metavar="USER", help="Login or numeric uid of the user.")
    ],
    *,
    tracker: TrackerClient,
) -> ComponentUserAccess:
    """Show what USER may do on a component (GET /components/{id}/permissions/users/{user})."""
    return tracker.components.user_permissions_get(component_id, user_id)


@app.command("group-permissions-get")
def group_permissions_get(
    component_id: ComponentIDArg,
    group_id: Annotated[int, typer.Argument(metavar="GROUP_ID", help="Numeric id of the group.")],
    *,
    tracker: TrackerClient,
) -> ComponentGroupAccess:
    """Show what GROUP_ID may do on a component (…/permissions/groups/{group})."""
    return tracker.components.group_permissions_get(component_id, group_id)
