"""`tracker bulk` commands — async mass update/move/transition (with ``--wait`` polling).

Each trigger returns a bulk-change ``{id, status}``. With ``--wait`` (default) the command
polls ``GET /bulkchange/{id}`` via :func:`ycli.yandex.polling.poll` until the status is
terminal, then prints the final status; with ``--no-wait`` it prints the created ``{id,
status}`` immediately.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.progress import spinner
from ycli.yandex.polling import poll
from ycli.yandex.tracker.bulk.models import BulkMove, BulkTransition, BulkUpdate
from ycli.yandex.tracker.utils import parse_fields

if TYPE_CHECKING:
    from ycli.yandex.tracker.bulk.models import BulkChange

app = typer.Typer(name="bulk", help="Tracker async bulk changes.", no_args_is_help=True)

BulkIdArg = Annotated[
    str, typer.Argument(metavar="BULK_ID", help="Bulk-change operation id from a trigger.")
]

IssueOpt = Annotated[
    list[str] | None,
    typer.Option("--issue", help="Issue key to include (repeatable; omit when using --query)."),
]
QueryOpt = Annotated[
    str,
    typer.Option("--query", help="Query-language filter selecting issues (instead of --issue)."),
]
ValueOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Field to set, key=value (JSON-coerced; repeatable)."),
]
NotifyOpt = Annotated[bool, typer.Option("--notify/--no-notify", help="Notify affected users.")]
WaitOpt = Annotated[
    bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
]


def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


app.callback()(_group)


def _issues(issue: list[str] | None, query: str) -> list[str] | str:
    """The ``issues`` body value: the query string when given, else the collected keys."""
    return query if query else (issue or [])


def _finish(app_ctx: AppContext, bulk: BulkChange, wait: bool) -> None:
    """Print ``bulk`` — after polling it to a terminal status first when ``wait`` is set.

    The wait is silent (default-on and potentially minutes long), so it is wrapped in a
    stderr spinner; the spinner is a no-op when stderr is not a terminal, so a piped run's
    stdout data stays byte-clean.
    """
    if wait and bulk.id is not None:
        bulk_id = bulk.id  # narrowed to str — the poll re-reads this operation
        with spinner("Waiting for bulk change…", console=app_ctx.stderr_console):
            bulk = poll(
                lambda: app_ctx.tracker.bulk.get(bulk_id),
                lambda change: change.is_terminal,
                sleep=lambda seconds: time.sleep(seconds),
            )
    Serializer.serialize(bulk, app_ctx.strategy, app_ctx.console)


@app.command()
def update(
    ctx: typer.Context,
    issue: IssueOpt = None,
    query: QueryOpt = "",
    field: ValueOpt = None,
    notify: NotifyOpt = False,
    wait: WaitOpt = True,
) -> None:
    """Mass-edit issues (POST /bulkchange/_update). Set fields with repeated -F key=value."""
    body = BulkUpdate(
        issues=_issues(issue, query), values=parse_fields(field), notify=notify or None
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    _finish(app_ctx, app_ctx.tracker.bulk.update(body=body), wait)


@app.command()
def move(
    ctx: typer.Context,
    queue: Annotated[str, typer.Argument(metavar="QUEUE", help="Target queue key, e.g. CHECK.")],
    issue: IssueOpt = None,
    query: QueryOpt = "",
    field: ValueOpt = None,
    move_all_fields: Annotated[
        bool, typer.Option("--move-all-fields", help="Carry versions/components/projects across.")
    ] = False,
    initial_status: Annotated[
        bool, typer.Option("--initial-status", help="Reset each issue's status to the initial one.")
    ] = False,
    notify: NotifyOpt = False,
    wait: WaitOpt = True,
) -> None:
    """Mass-move issues to another QUEUE (POST /bulkchange/_move)."""
    body = BulkMove(
        queue=queue,
        issues=_issues(issue, query),
        values=parse_fields(field) or None,
        move_all_fields=move_all_fields or None,
        initial_status=initial_status or None,
        notify=notify or None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    _finish(app_ctx, app_ctx.tracker.bulk.move(body=body), wait)


@app.command()
def transition(
    ctx: typer.Context,
    transition: Annotated[
        str, typer.Argument(metavar="TRANSITION", help="Transition id, e.g. close.")
    ],
    issue: IssueOpt = None,
    query: QueryOpt = "",
    field: ValueOpt = None,
    notify: NotifyOpt = False,
    wait: WaitOpt = True,
) -> None:
    """Mass status transition (POST /bulkchange/_transition). -F resolution=fixed for close."""
    body = BulkTransition(
        transition=transition,
        issues=_issues(issue, query),
        values=parse_fields(field) or None,
        notify=notify or None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    _finish(app_ctx, app_ctx.tracker.bulk.transition(body=body), wait)


@app.command()
def get(ctx: typer.Context, bulk_id: BulkIdArg) -> None:
    """Print the current status of bulk-change BULK_ID (GET /bulkchange/{id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.bulk.get(bulk_id), app_ctx.strategy, app_ctx.console)


@app.command()
def issues(ctx: typer.Context, bulk_id: BulkIdArg) -> None:
    """List issues that a bulk change failed on (GET /bulkchange/{id}/issues)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.bulk.issues(bulk_id), app_ctx.strategy, app_ctx.console)
