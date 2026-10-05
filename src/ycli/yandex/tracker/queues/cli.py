"""`tracker queues` commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueCreate,
    QueueField,
    QueueGroupAccess,
    QueuePermissions,
    QueuePermissionsUpdate,
    QueueTagRemove,
    QueueUserAccess,
    QueueVersionCreate,
    QueueVersionInfo,
    QueueVersionUpdate,
)
from ycli.yandex.tracker.typedefs import ExpandOpt, QueueIDArg

app = typer.Typer(name="queues", help="Tracker queues.", no_args_is_help=True)

VersionIDArg = Annotated[
    int, typer.Argument(metavar="VERSION_ID", help="Numeric id of the queue version.")
]
QueueFieldsOpt = Annotated[
    str | None, typer.Option(help="Comma-separated fields to return, e.g. name,dueDate,released.")
]


@app.command("list")
def list_(
    limit: LimitOption = None,
    all_: AllOption = False,
    expand: ExpandOpt = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[Queue]:
    """List all queues (auto-paginated over pages; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.queues.list(limit=cap, expand=expand)


@app.command()
def get(
    queue_id: Annotated[str, typer.Argument(help="Queue key (case-sensitive) or numeric id.")],
    expand: Annotated[
        str | None, typer.Option(help="Extra blocks to include, e.g. all or types,team,versions.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Queue:
    """Print one queue's settings for QUEUE_ID."""
    return tracker.queues.get(queue_id, expand=expand)


@app.command()
def tags_list(queue_id: QueueIDArg, *, tracker: TrackerClient) -> ItemList[str]:
    """List the tags added to QUEUE_ID."""
    return tracker.queues.tags_list(queue_id)


@app.command()
def versions_list(queue_id: QueueIDArg, *, tracker: TrackerClient) -> ItemList[QueueVersionInfo]:
    """List the versions defined on QUEUE_ID."""
    return tracker.queues.versions_list(queue_id)


@app.command()
def fields_list(queue_id: QueueIDArg, *, tracker: TrackerClient) -> ItemList[QueueField]:
    """List the required/local fields of QUEUE_ID."""
    return tracker.queues.fields_list(queue_id)


@app.command()
def create(
    key: Annotated[str, typer.Option(help="Key of the new queue (case-sensitive, e.g. DESIGN).")],
    name: Annotated[str, typer.Option(help="Human-readable name of the queue.")],
    lead: Annotated[str, typer.Option(help="Login or id of the queue owner (lead).")],
    default_type: Annotated[
        str, typer.Option("--default-type", help="Key/id of the default issue type.")
    ],
    default_priority: Annotated[
        str, typer.Option("--default-priority", help="Key/id of the default priority.")
    ],
    issue_type_config: Annotated[
        list[str] | None,
        typer.Option(
            "--issue-type-config",
            help='issueTypesConfig row as JSON, e.g. \'{"issueType":"task","workflow":"oicn"}\''
            " (repeatable).",
        ),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Queue:
    """Create a queue (POST /queues/)."""
    body = QueueCreate(
        key=key,
        name=name,
        lead=lead,
        default_type=default_type,
        default_priority=default_priority,
        issue_types_config=[json.loads(row) for row in issue_type_config]
        if issue_type_config
        else None,
    )
    return tracker.queues.create(body)


@app.command()
def delete(queue_id: QueueIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete QUEUE_ID (DELETE /queues/{queue_id})."""
    tracker.queues.delete(queue_id)
    return Ack.deleted("queue", queue_id)


@app.command()
def restore(queue_id: QueueIDArg, *, tracker: TrackerClient) -> Queue:
    """Restore a deleted QUEUE_ID (POST /queues/{queue_id}/_restore; admin only)."""
    return tracker.queues.restore(queue_id)


@app.command()
def permissions_update(
    queue_id: QueueIDArg,
    create: Annotated[
        str | None, typer.Option(help="Create-issue permission scope as a JSON object.")
    ] = None,
    write: Annotated[
        str | None, typer.Option(help="Edit-issue permission scope as a JSON object.")
    ] = None,
    read: Annotated[
        str | None, typer.Option(help="Read-issue permission scope as a JSON object.")
    ] = None,
    grant: Annotated[
        str | None, typer.Option(help="Change-settings permission scope as a JSON object.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> QueuePermissions:
    """Manage access to QUEUE_ID (PATCH /queues/{queue_id}/permissions).

    Each scope is a JSON object of users/groups/roles, e.g.
    --grant '{"roles": {"add": ["author"]}}'. Pass at least one scope.
    """
    body = QueuePermissionsUpdate(
        create=json.loads(create) if create is not None else None,
        write=json.loads(write) if write is not None else None,
        read=json.loads(read) if read is not None else None,
        grant=json.loads(grant) if grant is not None else None,
    )
    return tracker.queues.permissions_update(queue_id, body)


@app.command("tags-delete")
def tags_delete(
    queue_id: QueueIDArg,
    tag: Annotated[str, typer.Argument(help="Name of the tag to remove.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Remove TAG from QUEUE_ID (POST /queues/{queue_id}/tags/_remove; admin only)."""
    tracker.queues.tags_delete(queue_id, QueueTagRemove(tag=tag))
    return Ack.removed("tag", tag, from_=f"queue {queue_id}")


@app.command("versions-create")
def versions_create(
    queue: Annotated[str, typer.Option(help="Key of the queue to create the version in.")],
    name: Annotated[str, typer.Option(help="Name of the new version.")],
    description: Annotated[str | None, typer.Option(help="Description of the version.")] = None,
    start_date: Annotated[
        str | None, typer.Option("--start-date", help="Version start date (YYYY-MM-DD).")
    ] = None,
    due_date: Annotated[
        str | None, typer.Option("--due-date", help="Version due date (YYYY-MM-DD).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> QueueVersionInfo:
    """Create a queue version (POST /versions/)."""
    body = QueueVersionCreate(
        queue=queue,
        name=name,
        description=description,
        start_date=start_date,
        due_date=due_date,
    )
    return tracker.queues.versions_create(body)


@app.command("versions-get")
def versions_get(
    version_id: VersionIDArg, fields: QueueFieldsOpt = None, *, tracker: TrackerClient
) -> QueueVersionInfo:
    """Print queue version VERSION_ID (GET /versions/{id})."""
    return tracker.queues.versions_get(version_id, fields=fields)


@app.command("versions-update")
def versions_update(
    version_id: VersionIDArg,
    name: Annotated[str | None, typer.Option(help="New name of the version.")] = None,
    description: Annotated[str | None, typer.Option(help="New description of the version.")] = None,
    start_date: Annotated[
        str | None, typer.Option("--start-date", help="New version start date (YYYY-MM-DD).")
    ] = None,
    due_date: Annotated[
        str | None, typer.Option("--due-date", help="New version due date (YYYY-MM-DD).")
    ] = None,
    fields: QueueFieldsOpt = None,
    *,
    tracker: TrackerClient,
) -> QueueVersionInfo:
    """Edit queue version VERSION_ID (PATCH /versions/{id}); only the given options change."""
    body = QueueVersionUpdate(
        name=name,
        description=description,
        start_date=start_date,
        due_date=due_date,
    )
    return tracker.queues.versions_update(version_id, body, fields=fields)


@app.command("versions-delete")
def versions_delete(version_id: VersionIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete queue version VERSION_ID (DELETE /versions/{id})."""
    tracker.queues.versions_delete(version_id)
    return Ack.deleted("version", version_id)


@app.command("user-permissions-get")
def user_permissions_get(
    queue_id: QueueIDArg,
    user_id: Annotated[
        str, typer.Argument(metavar="USER", help="Login or numeric uid of the user.")
    ],
    *,
    tracker: TrackerClient,
) -> QueueUserAccess:
    """Show what USER may do in QUEUE_ID (GET /queues/{id}/permissions/users/{user})."""
    return tracker.queues.user_permissions_get(queue_id, user_id)


@app.command("group-permissions-get")
def group_permissions_get(
    queue_id: QueueIDArg,
    group_id: Annotated[int, typer.Argument(metavar="GROUP_ID", help="Numeric id of the group.")],
    *,
    tracker: TrackerClient,
) -> QueueGroupAccess:
    """Show what GROUP_ID may do in QUEUE_ID (GET /queues/{id}/permissions/groups/{group})."""
    return tracker.queues.group_permissions_get(queue_id, group_id)
