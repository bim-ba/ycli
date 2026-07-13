"""`tracker queues` commands."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.queues.models import (
    QueueCreate,
    QueuePermissionsUpdate,
    QueueTagRemove,
    QueueVersionCreate,
)

app = typer.Typer(name="queues", help="Tracker queues.", no_args_is_help=True)

QueueIdArg = Annotated[
    str, typer.Argument(metavar="QUEUE_ID", help="Queue key (case-sensitive) or numeric id.")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    limit: LimitOption = 0,
    all_: AllOption = False,
) -> None:
    """List all queues (auto-paginated over pages; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(app_ctx.tracker.queues.list(limit=cap), app_ctx.strategy, app_ctx.console)


@app.command()
def get(
    ctx: typer.Context,
    queue_id: Annotated[str, typer.Argument(help="Queue key (case-sensitive) or numeric id.")],
    expand: Annotated[
        str, typer.Option(help="Extra blocks to include, e.g. all or types,team,versions.")
    ] = "",
) -> None:
    """Print one queue's settings for QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.queues.get(queue_id, expand=expand or None),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def tags(ctx: typer.Context, queue_id: QueueIdArg) -> None:
    """List the tags added to QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.queues.tags(queue_id), app_ctx.strategy, app_ctx.console)


@app.command()
def versions(ctx: typer.Context, queue_id: QueueIdArg) -> None:
    """List the versions defined on QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.queues.versions(queue_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def fields(ctx: typer.Context, queue_id: QueueIdArg) -> None:
    """List the required/local fields of QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.queues.fields(queue_id), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
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
) -> None:
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
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.queues.create(body), app_ctx.strategy, app_ctx.console)


@app.command()
def delete(ctx: typer.Context, queue_id: QueueIdArg) -> None:
    """Delete QUEUE_ID (DELETE /queues/{queue_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.queues.delete(queue_id)
    Serializer.serialize(Ack.deleted("queue", queue_id), app_ctx.strategy, app_ctx.console)


@app.command()
def restore(ctx: typer.Context, queue_id: QueueIdArg) -> None:
    """Restore a deleted QUEUE_ID (POST /queues/{queue_id}/_restore; admin only)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.queues.restore(queue_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def permissions(
    ctx: typer.Context,
    queue_id: QueueIdArg,
    create: Annotated[
        str, typer.Option(help="Create-issue permission scope as a JSON object.")
    ] = "",
    write: Annotated[str, typer.Option(help="Edit-issue permission scope as a JSON object.")] = "",
    read: Annotated[str, typer.Option(help="Read-issue permission scope as a JSON object.")] = "",
    grant: Annotated[
        str, typer.Option(help="Change-settings permission scope as a JSON object.")
    ] = "",
) -> None:
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
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.queues.set_permissions(queue_id, body), app_ctx.strategy, app_ctx.console
    )


@app.command("tag-remove")
def tag_remove(
    ctx: typer.Context,
    queue_id: QueueIdArg,
    tag: Annotated[str, typer.Argument(help="Name of the tag to remove.")],
) -> None:
    """Remove TAG from QUEUE_ID (POST /queues/{queue_id}/tags/_remove; admin only)."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.queues.tag_remove(queue_id, QueueTagRemove(tag=tag))
    Serializer.serialize(
        Ack.removed("tag", tag, from_=f"queue {queue_id}"), app_ctx.strategy, app_ctx.console
    )


@app.command("version-create")
def version_create(
    ctx: typer.Context,
    queue: Annotated[str, typer.Option(help="Key of the queue to create the version in.")],
    name: Annotated[str, typer.Option(help="Name of the new version.")],
    description: Annotated[str, typer.Option(help="Description of the version.")] = "",
    start_date: Annotated[
        str, typer.Option("--start-date", help="Version start date (YYYY-MM-DD).")
    ] = "",
    due_date: Annotated[
        str, typer.Option("--due-date", help="Version due date (YYYY-MM-DD).")
    ] = "",
) -> None:
    """Create a queue version (POST /versions/)."""
    body = QueueVersionCreate(
        queue=queue,
        name=name,
        description=description or None,
        start_date=start_date or None,
        due_date=due_date or None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.queues.version_create(body), app_ctx.strategy, app_ctx.console
    )
