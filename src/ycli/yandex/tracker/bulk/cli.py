"""`tracker bulk` commands — async mass update/move/transition (with ``--wait`` polling).

Each trigger returns a bulk-change ``{id, status}``. With ``--wait`` (default) the command
polls ``GET /bulkchange/{id}`` via :func:`ycli.cli.progress.wait_for` until the status is
terminal, then prints the final status; with ``--no-wait`` it prints the created ``{id,
status}`` immediately.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.fields import parse_fields
from ycli.cli.progress import wait_for
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.bulk.models import (
    BulkChange,
    BulkIssueResult,
    BulkMove,
    BulkTransition,
    BulkUpdate,
)
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="bulk", help="Tracker async bulk changes.", no_args_is_help=True)

BulkIDArg = Annotated[
    str, typer.Argument(metavar="BULK_ID", help="Bulk-change operation id from a trigger.")
]

IssueOpt = Annotated[
    list[str] | None,
    typer.Option("--issue", help="Issue key to include (repeatable; omit when using --query)."),
]
QueryOpt = Annotated[
    str | None,
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


def _issues(issue: list[str] | None, query: str | None) -> list[str] | str:
    """The ``issues`` body value: the query string when given, else the collected keys."""
    return query if query is not None else (issue or [])


def _finish(tracker: TrackerClient, config: AppConfig, bulk: BulkChange, wait: bool) -> BulkChange:
    """``bulk`` — after polling it to a terminal status first when ``wait`` is set.

    The wait is default-on and potentially minutes long, so it goes through the shared
    :func:`ycli.cli.progress.wait_for` — a stderr spinner on a terminal, byte-clean
    silence when piped.
    """
    if wait and bulk.id is not None:
        bulk_id = bulk.id  # narrowed to str — the poll re-reads this operation
        bulk = wait_for(
            lambda: tracker.bulk.get(bulk_id),
            lambda change: change.is_terminal,
            message="Waiting for bulk change…",
            max_wait_seconds=config.http.max_wait_seconds,
        )
    return bulk


@app.command()
def update(
    issue: IssueOpt = None,
    query: QueryOpt = None,
    field: ValueOpt = None,
    notify: NotifyOpt = False,
    wait: WaitOpt = True,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> BulkChange:
    """Mass-edit issues (POST /bulkchange/_update). Set fields with repeated -F key=value."""
    body = BulkUpdate(
        issues=_issues(issue, query), values=parse_fields(field), notify=notify or None
    )
    return _finish(tracker, config, tracker.bulk.update(body=body, notify=notify or None), wait)


@app.command()
def move(
    queue: Annotated[str, typer.Argument(metavar="QUEUE", help="Target queue key, e.g. CHECK.")],
    issue: IssueOpt = None,
    query: QueryOpt = None,
    field: ValueOpt = None,
    move_all_fields: Annotated[
        bool, typer.Option("--move-all-fields", help="Carry versions/components/projects across.")
    ] = False,
    initial_status: Annotated[
        bool, typer.Option("--initial-status", help="Reset each issue's status to the initial one.")
    ] = False,
    notify: NotifyOpt = False,
    wait: WaitOpt = True,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> BulkChange:
    """Mass-move issues to another QUEUE (POST /bulkchange/_move)."""
    body = BulkMove(
        queue=queue,
        issues=_issues(issue, query),
        values=parse_fields(field) or None,
        moveAllFields=move_all_fields or None,
        initialStatus=initial_status or None,
        notify=notify or None,
    )
    return _finish(tracker, config, tracker.bulk.move(body=body, notify=notify or None), wait)


@app.command()
def transition(
    transition: Annotated[
        str, typer.Argument(metavar="TRANSITION", help="Transition id, e.g. close.")
    ],
    issue: IssueOpt = None,
    query: QueryOpt = None,
    field: ValueOpt = None,
    notify: NotifyOpt = False,
    wait: WaitOpt = True,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> BulkChange:
    """Mass status transition (POST /bulkchange/_transition). -F resolution=fixed for close."""
    body = BulkTransition(
        transition=transition,
        issues=_issues(issue, query),
        values=parse_fields(field) or None,
        notify=notify or None,
    )
    return _finish(tracker, config, tracker.bulk.transition(body=body, notify=notify or None), wait)


@app.command()
def get(bulk_id: BulkIDArg, *, tracker: TrackerClient) -> BulkChange:
    """Print the current status of bulk-change BULK_ID (GET /bulkchange/{id})."""
    return tracker.bulk.get(bulk_id)


@app.command()
def issues_list(bulk_id: BulkIDArg, *, tracker: TrackerClient) -> ItemList[BulkIssueResult]:
    """List issues that a bulk change failed on (GET /bulkchange/{id}/issues)."""
    return tracker.bulk.issues_list(bulk_id)
