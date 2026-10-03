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

app = typer.Typer(name="queues", help="Tracker queues.", no_args_is_help=True)

QueueIdArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]
VersionIdArg = Annotated[
    int, typer.Argument(metavar="VERSION_ID", help="Numeric id of the queue version.")
]
FieldsOpt = Annotated[
    str, typer.Option(help="Comma-separated fields to return, e.g. name,dueDate,released.")
]


@app.command("list")
def list_(
    limit: LimitOption = 0, all_: AllOption = False, *, config: AppConfig, tracker: TrackerClient
) -> ItemList[Queue]:
    """List all queues (auto-paginated over pages; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.queues.list(limit=cap)


@app.command()
def get(
    queue_id: Annotated[str, typer.Argument(help="Queue key (case-sensitive) or numeric id.")],
    expand: Annotated[
        str, typer.Option(help="Extra blocks to include, e.g. all or types,team,versions.")
    ] = "",
    *,
    tracker: TrackerClient,
) -> Queue:
    """Print one queue's settings for QUEUE_ID."""
    return tracker.queues.get(queue_id, expand=expand or None)


@app.command()
def tags_list(queue_id: QueueIdArg, *, tracker: TrackerClient) -> ItemList[str]:
    """List the tags added to QUEUE_ID."""
    return tracker.queues.tags(queue_id)


@app.command()
def versions_list(queue_id: QueueIdArg, *, tracker: TrackerClient) -> ItemList[QueueVersionInfo]:
    """List the versions defined on QUEUE_ID."""
    return tracker.queues.versions(queue_id)


@app.command()
def fields_list(queue_id: QueueIdArg, *, tracker: TrackerClient) -> ItemList[QueueField]:
    """List the required/local fields of QUEUE_ID."""
    return tracker.queues.fields(queue_id)


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
def delete(queue_id: QueueIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete QUEUE_ID (DELETE /queues/{queue_id})."""
    tracker.queues.delete(queue_id)
    return Ack.deleted("queue", queue_id)


@app.command()
def restore(queue_id: QueueIdArg, *, tracker: TrackerClient) -> Queue:
    """Restore a deleted QUEUE_ID (POST /queues/{queue_id}/_restore; admin only)."""
    return tracker.queues.restore(queue_id)


@app.command()
def set_permissions(
    queue_id: QueueIdArg,
    create: Annotated[
        str, typer.Option(help="Create-issue permission scope as a JSON object.")
    ] = "",
    write: Annotated[str, typer.Option(help="Edit-issue permission scope as a JSON object.")] = "",
    read: Annotated[str, typer.Option(help="Read-issue permission scope as a JSON object.")] = "",
    grant: Annotated[
        str, typer.Option(help="Change-settings permission scope as a JSON object.")
    ] = "",
    *,
    tracker: TrackerClient,
) -> QueuePermissions:
    """Manage access to QUEUE_ID (PATCH /queues/{queue_id}/permissions).

    Each scope is a JSON object of users/groups/roles, e.g.
    --grant '{"roles": {"add": ["author"]}}'. Pass at least one scope.
    """
    body = QueuePermissionsUpdate(
        create=json.loads(create) if create else None,
        write=json.loads(write) if write else None,
        read=json.loads(read) if read else None,
        grant=json.loads(grant) if grant else None,
    )
    return tracker.queues.set_permissions(queue_id, body)


@app.command("tag-remove")
def tag_remove(
    queue_id: QueueIdArg,
    tag: Annotated[str, typer.Argument(help="Name of the tag to remove.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Remove TAG from QUEUE_ID (POST /queues/{queue_id}/tags/_remove; admin only)."""
    tracker.queues.tag_remove(queue_id, QueueTagRemove(tag=tag))
    return Ack.removed("tag", tag, from_=f"queue {queue_id}")


@app.command("version-create")
def version_create(
    queue: Annotated[str, typer.Option(help="Key of the queue to create the version in.")],
    name: Annotated[str, typer.Option(help="Name of the new version.")],
    description: Annotated[str, typer.Option(help="Description of the version.")] = "",
    start_date: Annotated[
        str, typer.Option("--start-date", help="Version start date (YYYY-MM-DD).")
    ] = "",
    due_date: Annotated[
        str, typer.Option("--due-date", help="Version due date (YYYY-MM-DD).")
    ] = "",
    *,
    tracker: TrackerClient,
) -> QueueVersionInfo:
    """Create a queue version (POST /versions/)."""
    body = QueueVersionCreate(
        queue=queue,
        name=name,
        description=description or None,
        start_date=start_date or None,
        due_date=due_date or None,
    )
    return tracker.queues.version_create(body)


@app.command("version-get")
def version_get(
    version_id: VersionIdArg, fields: FieldsOpt = "", *, tracker: TrackerClient
) -> QueueVersionInfo:
    """Print queue version VERSION_ID (GET /versions/{id})."""
    return tracker.queues.version_get(version_id, fields=fields or None)


@app.command("version-update")
def version_update(
    version_id: VersionIdArg,
    name: Annotated[str, typer.Option(help="New name of the version.")] = "",
    description: Annotated[str, typer.Option(help="New description of the version.")] = "",
    start_date: Annotated[
        str, typer.Option("--start-date", help="New version start date (YYYY-MM-DD).")
    ] = "",
    due_date: Annotated[
        str, typer.Option("--due-date", help="New version due date (YYYY-MM-DD).")
    ] = "",
    fields: FieldsOpt = "",
    *,
    tracker: TrackerClient,
) -> QueueVersionInfo:
    """Edit queue version VERSION_ID (PATCH /versions/{id}); only the given options change."""
    body = QueueVersionUpdate(
        name=name or None,
        description=description or None,
        start_date=start_date or None,
        due_date=due_date or None,
    )
    return tracker.queues.version_edit(version_id, body, fields=fields or None)


@app.command("version-delete")
def version_delete(version_id: VersionIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete queue version VERSION_ID (DELETE /versions/{id})."""
    tracker.queues.version_delete(version_id)
    return Ack.deleted("version", version_id)


@app.command("user-permissions-get")
def user_permissions_get(
    queue_id: QueueIdArg,
    user_id: Annotated[
        str, typer.Argument(metavar="USER", help="Login or numeric uid of the user.")
    ],
    *,
    tracker: TrackerClient,
) -> QueueUserAccess:
    """Show what USER may do in QUEUE_ID (GET /queues/{id}/permissions/users/{user})."""
    return tracker.queues.user_permissions(queue_id, user_id)


@app.command("group-permissions-get")
def group_permissions_get(
    queue_id: QueueIdArg,
    group_id: Annotated[int, typer.Argument(metavar="GROUP_ID", help="Numeric id of the group.")],
    *,
    tracker: TrackerClient,
) -> QueueGroupAccess:
    """Show what GROUP_ID may do in QUEUE_ID (GET /queues/{id}/permissions/groups/{group})."""
    return tracker.queues.group_permissions(queue_id, group_id)
