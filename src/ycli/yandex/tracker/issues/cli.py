"""`tracker issues` commands — argument-based; dumps full pydantic models as JSON."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.fields import parse_fields
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.models import (
    Issue,
    IssueCreate,
    IssueSearch,
    IssueUpdate,
    ScrollClear,
    count_body,
    filter_body,
)
from ycli.yandex.tracker.typedefs import (
    ExpandOpt,
    KeyArg,
    NotifyAuthorOpt,
    NotifyOpt,
    ReplyFieldsOpt,
)

app = typer.Typer(name="issues", help="Tracker issues.", no_args_is_help=True)

FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Extra field key=value (JSON-coerced; repeatable)."),
]


def _key(value: str) -> dict[str, str] | None:
    """The ``{"key": …}`` object Tracker takes for a type or priority; ``None`` when not given.

    Examples:
        >>> _key("task"), _key("")
        ({'key': 'task'}, None)
    """
    return {"key": value} if value else None


@app.command()
def get(
    key: KeyArg, expand: ExpandOpt = "", fields: ReplyFieldsOpt = "", *, tracker: TrackerClient
) -> Issue:
    """Print a single issue (full model) for KEY."""
    return tracker.issues.get(key, expand=expand or None, fields=fields or None)


@app.command("list")
def list_(
    queue: Annotated[str, typer.Option(help="Queue key.")] = "",
    status: Annotated[str, typer.Option(help="Status key.")] = "",
    assignee: Annotated[str, typer.Option(help="Assignee login.")] = "",
    epic: Annotated[str, typer.Option(help="Epic key.")] = "",
    type_: Annotated[str, typer.Option("--type", help="Issue type key.")] = "",
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[Issue]:
    """List issues matching the supplied filters (auto-paginated; --all for everything)."""
    body = filter_body(queue=queue, status=status, assignee=assignee, epic=epic, type_=type_)
    return tracker.issues.search(body, limit=config.http.cap(limit, all_=all_))


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="TQL query.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    expand: ExpandOpt = "",
    scroll_type: Annotated[
        str, typer.Option(help="sorted or unsorted: scroll through the results (no 10 000 cap).")
    ] = "",
    per_scroll: Annotated[
        int | None, typer.Option(help="Issues per scroll page (1000 at most).")
    ] = None,
    scroll_ttl_millis: Annotated[
        int | None, typer.Option(help="How long the scroll stays open, in milliseconds.")
    ] = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[Issue]:
    """Search issues by a TQL query string (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.issues.search(
        IssueSearch(query=query),
        limit=cap,
        expand=expand or None,
        scroll_type=scroll_type or None,
        per_scroll=per_scroll,
        scroll_ttl_millis=scroll_ttl_millis,
    )


@app.command()
def count(
    query: Annotated[str, typer.Option(help="TQL query (mutually exclusive with filters).")] = "",
    queue: Annotated[str, typer.Option(help="Queue key.")] = "",
    status: Annotated[str, typer.Option(help="Status key.")] = "",
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
    type_: Annotated[str, typer.Option("--type", help="Issue type key, e.g. task.")] = "",
    priority: Annotated[str, typer.Option(help="Priority key, e.g. normal.")] = "",
    parent: Annotated[str, typer.Option(help="Parent issue key.")] = "",
    description: Annotated[
        str | None, typer.Option(help='Markdown body — pass "$(cat file.md)".')
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    field: FieldOpt = None,
    notify: NotifyOpt = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Create an issue (POST /issues/). type/priority wrap to {"key": …}; queue/parent stay bare."""
    named = IssueCreate(
        queue=queue,
        summary=summary,
        type=_key(type_),
        priority=_key(priority),
        parent=parent or None,
        description=description,
        tags=tag or None,
    )
    # The named options, then whatever --field adds or overrides.
    body = IssueCreate.model_validate(named.model_dump(exclude_none=True) | parse_fields(field))
    return tracker.issues.create(body=body, notify=notify)


@app.command()
def update(
    key: KeyArg,
    summary: Annotated[str, typer.Option(help="New summary.")] = "",
    type_: Annotated[str, typer.Option("--type", help="New issue type key.")] = "",
    priority: Annotated[str, typer.Option(help="New priority key.")] = "",
    parent: Annotated[str, typer.Option(help="New parent issue key.")] = "",
    description: Annotated[
        str | None,
        typer.Option(help='New markdown body — pass "$(cat file.md)"; "" clears it.'),
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    field: FieldOpt = None,
    *,
    tracker: TrackerClient,
) -> Issue:
    """Update issue KEY (PATCH /issues/{key}) — only supplied fields are sent."""
    named = IssueUpdate(
        summary=summary or None,
        type=_key(type_),
        priority=_key(priority),
        parent=parent or None,
        description=description,
        tags=tag or None,
    )
    body = IssueUpdate.model_validate(named.model_dump(exclude_none=True) | parse_fields(field))
    return tracker.issues.update(key, body=body)


@app.command()
def move(
    key: KeyArg,
    queue: Annotated[str, typer.Argument(metavar="QUEUE", help="Target queue key, e.g. NEW.")],
    expand: ExpandOpt = "",
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
    """Move issue KEY to another QUEUE (POST /issues/{key}/_move?queue=QUEUE)."""
    return tracker.issues.move(
        key,
        queue,
        expand=expand or None,
        initial_status=initial_status,
        move_all_fields=move_all_fields,
        notify=notify,
        notify_author=notify_author,
    )


@app.command()
def suggest(
    text: Annotated[str, typer.Argument(metavar="INPUT", help="Text fragment to match in titles.")],
    queue: Annotated[str, typer.Option(help="Key of the queue to search in.")] = "",
    full: Annotated[
        bool | None,
        typer.Option(
            "--full/--no-full",
            help="Return each issue in full; needed for --fields, --expand, --embed.",
        ),
    ] = None,
    fields: ReplyFieldsOpt = "",
    expand: ExpandOpt = "",
    embed: Annotated[str, typer.Option(help="Blocks of --expand to return in more detail.")] = "",
    *,
    tracker: TrackerClient,
) -> ItemList[Issue]:
    """Suggest issues whose summary contains INPUT (GET /issues/_suggest?input=INPUT)."""
    return tracker.issues.suggest(
        text,
        queue=queue or None,
        full=full,
        fields=fields or None,
        expand=expand or None,
        embed=embed or None,
    )


@app.command("scroll-clear")
def scroll_clear(
    pair: Annotated[
        list[str] | None,
        typer.Option("--pair", help="scrollId=scrollToken pair to release (repeatable)."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Ack:
    """Release search-scroll resources (POST /system/search/scroll/_clear).

    Pass each ``--pair scrollId=scrollToken`` from a scrolled ``issues search``.
    """
    tracker.issues.scroll_clear(ScrollClear(parse_fields(pair)))
    return Ack.cleared("search scroll resources")
