"""`tracker issues` commands — argument-based; dumps full pydantic models as JSON."""

from typing import Annotated

import typer

from ycli.cli.fields import parse_fields
from ycli.cli.progress import wait_for
from ycli.cli.typedefs import AllOption, LimitOption, NextOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.bulk.models import BulkChange, BulkMove, BulkTransition, BulkUpdate
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.models import (
    ImportTask,
    Issue,
    IssueCreate,
    IssueSearch,
    IssueUpdate,
    ScrollType,
    count_body,
    filter_body,
)
from ycli.yandex.tracker.typedefs import (
    ExpandOpt,
    ImportCreatedAtOpt,
    ImportCreatedByOpt,
    IssueKeyArg,
    NotifyAuthorOpt,
    NotifyOpt,
    ReplyFieldsOpt,
)

app = typer.Typer(name="issues", help="Tracker issues.", no_args_is_help=True)


def _key(value: str | None) -> dict[str, str] | None:
    """The ``{"key": …}`` object Tracker takes for a type or priority; ``None`` when not given.

    Examples:
        >>> _key("task"), _key(None)
        ({'key': 'task'}, None)
    """
    return {"key": value} if value is not None else None


@app.command()
def get(
    issue_key: IssueKeyArg,
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Print a single issue (full model) for ISSUE_KEY."""
    return tracker.issues.get(issue_key, expand=expand, fields=fields)


@app.command("list")
def list_(
    queue: Annotated[str | None, typer.Option(help="Queue key.")] = None,
    status: Annotated[str | None, typer.Option(help="Status key.")] = None,
    assignee: Annotated[str | None, typer.Option(help="Assignee login.")] = None,
    epic: Annotated[str | None, typer.Option(help="Epic key.")] = None,
    issue_type: Annotated[str | None, typer.Option("--issue-type", help="Issue type key.")] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> Listing[Issue]:
    """List issues matching the supplied filters (auto-paginated; --all for everything)."""
    body = filter_body(queue=queue, status=status, assignee=assignee, epic=epic, type_=issue_type)
    return tracker.issues.search(body, limit=config.http.cap(limit, all_=all_), next=next_)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="TQL query.")],
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    expand: ExpandOpt = None,
    scroll_type: Annotated[
        str | None,
        values_option(ScrollType, help="Scroll through the results (no 10 000 cap)."),
    ] = None,
    per_scroll: Annotated[
        int | None, typer.Option(help="Issues per scroll page (1000 at most).")
    ] = None,
    scroll_ttl_millis: Annotated[
        int | None, typer.Option(help="How long the scroll stays open, in milliseconds.")
    ] = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> Listing[Issue]:
    """Search issues by a TQL query string (auto-paginated; --all for everything).

    A token of a scroll (--scroll-type) works once: used again, it gives the portion after.
    """
    cap = config.http.cap(limit, all_=all_)
    return tracker.issues.search(
        IssueSearch(query=query),
        limit=cap,
        next=next_,
        expand=expand,
        scroll_type=scroll_type,
        per_scroll=per_scroll,
        scroll_ttl_millis=scroll_ttl_millis,
    )


@app.command()
def count(
    query: Annotated[
        str | None, typer.Option(help="TQL query (mutually exclusive with filters).")
    ] = None,
    queue: Annotated[str | None, typer.Option(help="Queue key.")] = None,
    status: Annotated[str | None, typer.Option(help="Status key.")] = None,
    *,
    tracker: TrackerClient,
) -> int:
    """Count issues matching a TQL query or filters (bare integer).

    With no ``--query`` and no filters this sends an empty filter — the API then counts
    EVERY issue in the org. Pass ``--queue``/``--status`` (or ``--query``) to narrow.
    """
    return tracker.issues.count(body=count_body(query=query, queue=queue, status=status))


@app.command()
def create(
    queue: Annotated[str, typer.Option(help="Target queue key.")],
    summary: Annotated[str, typer.Option(help="Issue summary (title).")],
    type_: Annotated[str | None, typer.Option("--type", help="Issue type key, e.g. task.")] = None,
    priority: Annotated[str | None, typer.Option(help="Priority key, e.g. normal.")] = None,
    parent: Annotated[str | None, typer.Option(help="Parent issue key.")] = None,
    description: Annotated[
        str | None, typer.Option(help='Markdown body — pass "$(cat file.md)".')
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    notify: NotifyOpt = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Create an issue (POST /issues/). type/priority wrap to {"key": …}; queue/parent stay bare."""
    body = IssueCreate(
        queue=queue,
        summary=summary,
        type=_key(type_),
        priority=_key(priority),
        parent=parent,
        description=description,
        tags=tag,
    )
    return tracker.issues.create(body=body, notify=notify)


@app.command()
def update(
    issue_key: IssueKeyArg,
    summary: Annotated[str | None, typer.Option(help="New summary.")] = None,
    type_: Annotated[str | None, typer.Option("--type", help="New issue type key.")] = None,
    priority: Annotated[str | None, typer.Option(help="New priority key.")] = None,
    parent: Annotated[str | None, typer.Option(help="New parent issue key.")] = None,
    description: Annotated[
        str | None,
        typer.Option(help='New markdown body — pass "$(cat file.md)"; "" clears it.'),
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Update issue ISSUE_KEY (PATCH /issues/{key}) — only supplied fields are sent."""
    body = IssueUpdate(
        summary=summary,
        type=_key(type_),
        priority=_key(priority),
        parent=parent,
        description=description,
        tags=tag,
    )
    return tracker.issues.update(issue_key, body=body)


@app.command()
def move(
    issue_key: IssueKeyArg,
    queue: Annotated[str, typer.Argument(metavar="QUEUE", help="Target queue key, e.g. NEW.")],
    expand: ExpandOpt = None,
    initial_status: Annotated[
        bool | None,
        typer.Option(
            "--initial-status/--no-initial-status",
            help="Reset the status to the new queue's initial one.",
        ),
    ] = None,
    move_all_fields: Annotated[
        bool | None,
        typer.Option(
            "--move-all-fields/--no-move-all-fields",
            help="Keep the versions, components and projects the new queue also has.",
        ),
    ] = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Move issue ISSUE_KEY to another QUEUE (POST /issues/{key}/_move?queue=QUEUE)."""
    return tracker.issues.move(
        issue_key,
        queue,
        expand=expand,
        initial_status=initial_status,
        move_all_fields=move_all_fields,
        notify=notify,
        notify_author=notify_author,
    )


@app.command()
def suggest(
    text: Annotated[str, typer.Argument(metavar="INPUT", help="Text fragment to match in titles.")],
    queue: Annotated[str | None, typer.Option(help="Key of the queue to search in.")] = None,
    full: Annotated[
        bool | None,
        typer.Option(
            "--full/--no-full",
            help="Return each issue in full; needed for --fields, --expand, --embed.",
        ),
    ] = None,
    fields: ReplyFieldsOpt = None,
    expand: ExpandOpt = None,
    embed: Annotated[
        str | None, typer.Option(help="Blocks of --expand to return in more detail.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Issue]:
    """Suggest issues whose summary contains INPUT (GET /issues/_suggest?input=INPUT)."""
    return tracker.issues.suggest(
        text,
        queue=queue,
        full=full,
        fields=fields,
        expand=expand,
        embed=embed,
    )


@app.command("scroll-clear")
def scroll_clear(
    next_: Annotated[
        str,
        typer.Option(
            "--next",
            metavar="TOKEN",
            help="The token a search by a scroll printed: it names the scroll to release.",
        ),
    ],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Release the scroll of a search before it expires (POST /system/search/scroll/_clear).

    Only ``issues search --scroll-type`` has something to release; after this its token goes
    on nowhere.
    """
    tracker.issues.scroll_clear(next_)
    return Ack.cleared("search scroll resources")


BulkIssueOpt = Annotated[
    list[str] | None,
    typer.Option("--issue", help="Issue key to include (repeatable; omit when using --query)."),
]
BulkQueryOpt = Annotated[
    str | None,
    typer.Option("--query", help="Query-language filter selecting issues (instead of --issue)."),
]
BulkValueOpt = Annotated[
    list[str] | None,
    typer.Option(
        "--field",
        "-F",
        help="Field to set, key=value (JSON-coerced; repeatable). key[sub]=value nests, and "
        "key=@FILE (@- for stdin) gives the file's text; a string that starts with @ goes in "
        "JSON quotes.",
    ),
]
BulkNotifyOpt = Annotated[
    bool | None, typer.Option("--notify/--no-notify", help="Notify affected users.")
]
BulkWaitOpt = Annotated[
    bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
]


def _bulk_issues(issue: list[str] | None, query: str | None) -> list[str] | str:
    """The ``issues`` body value: the query string when given, else the collected keys."""
    return query if query is not None else (issue or [])


def _bulk_finish(
    tracker: TrackerClient, config: AppConfig, bulk: BulkChange, wait: bool
) -> BulkChange:
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


@app.command("update-bulk")
def update_bulk(
    issue: BulkIssueOpt = None,
    query: BulkQueryOpt = None,
    field: BulkValueOpt = None,
    notify: BulkNotifyOpt = None,
    wait: BulkWaitOpt = True,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> BulkChange:
    """Mass-edit issues (POST /bulkchange/_update). Set fields with repeated -F key=value."""
    body = BulkUpdate(
        issues=_bulk_issues(issue, query),
        values=parse_fields(field, structured=True),
        notify=notify,
    )
    started = tracker.issues.update_bulk(body=body, notify=notify)
    return _bulk_finish(tracker, config, started, wait)


@app.command("move-bulk")
def move_bulk(
    queue: Annotated[str, typer.Argument(metavar="QUEUE", help="Target queue key, e.g. CHECK.")],
    issue: BulkIssueOpt = None,
    query: BulkQueryOpt = None,
    field: BulkValueOpt = None,
    move_all_fields: Annotated[
        bool | None,
        typer.Option(
            "--move-all-fields/--no-move-all-fields",
            help="Carry versions/components/projects across.",
        ),
    ] = None,
    initial_status: Annotated[
        bool | None,
        typer.Option(
            "--initial-status/--no-initial-status",
            help="Reset each issue's status to the initial one.",
        ),
    ] = None,
    notify: BulkNotifyOpt = None,
    wait: BulkWaitOpt = True,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> BulkChange:
    """Mass-move issues to another QUEUE (POST /bulkchange/_move)."""
    body = BulkMove(
        queue=queue,
        issues=_bulk_issues(issue, query),
        values=parse_fields(field, structured=True) or None,
        moveAllFields=move_all_fields,
        initialStatus=initial_status,
        notify=notify,
    )
    started = tracker.issues.move_bulk(body=body, notify=notify)
    return _bulk_finish(tracker, config, started, wait)


@app.command("transition-bulk")
def transition_bulk(
    transition: Annotated[
        str, typer.Argument(metavar="TRANSITION", help="Transition id, e.g. close.")
    ],
    issue: BulkIssueOpt = None,
    query: BulkQueryOpt = None,
    field: BulkValueOpt = None,
    notify: BulkNotifyOpt = None,
    wait: BulkWaitOpt = True,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> BulkChange:
    """Mass status transition (POST /bulkchange/_transition). -F resolution=fixed for close."""
    body = BulkTransition(
        transition=transition,
        issues=_bulk_issues(issue, query),
        values=parse_fields(field, structured=True) or None,
        notify=notify,
    )
    started = tracker.issues.transition_bulk(body=body, notify=notify)
    return _bulk_finish(tracker, config, started, wait)


@app.command("import")
def import_(
    queue: Annotated[str, typer.Option(help="Target queue key.")],
    summary: Annotated[str, typer.Option(help="Issue title.")],
    created_at: ImportCreatedAtOpt,
    created_by: ImportCreatedByOpt,
    key: Annotated[
        str | None, typer.Option(help="Explicit issue key (must belong to the queue).")
    ] = None,
    description: Annotated[str | None, typer.Option(help="Issue description (YFM).")] = None,
    assignee: Annotated[str | None, typer.Option(help="Assignee login or id.")] = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Import an issue preserving its history (POST /issues/_import)."""
    body = ImportTask(
        queue=queue,
        summary=summary,
        createdAt=created_at,
        createdBy=created_by,
        key=key,
        description=description,
        assignee=assignee,
    )
    return tracker.issues.import_(body=body)
