"""`tracker queues` commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.queues.models import (
    Queue,
    QueueCreate,
    QueueFieldList,
    QueueList,
    QueuePermissions,
    QueuePermissionsUpdate,
    QueueTagList,
    QueueTagRemove,
    QueueVersionCreate,
    QueueVersionInfo,
    QueueVersionInfoList,
)

app = typer.Typer(name="queues", help="Tracker queues.", no_args_is_help=True)

QueueIdArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]


@app.command("list")
def list_(
    limit: LimitOption = 0, all_: AllOption = False, *, config: AppConfig, tracker: TrackerClient
) -> QueueList:
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
def tags(queue_id: QueueIdArg, *, tracker: TrackerClient) -> QueueTagList:
    """List the tags added to QUEUE_ID."""
    return tracker.queues.tags(queue_id)


@app.command()
def versions(queue_id: QueueIdArg, *, tracker: TrackerClient) -> QueueVersionInfoList:
    """List the versions defined on QUEUE_ID."""
    return tracker.queues.versions(queue_id)


@app.command()
def fields(queue_id: QueueIdArg, *, tracker: TrackerClient) -> QueueFieldList:
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
def permissions(
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
