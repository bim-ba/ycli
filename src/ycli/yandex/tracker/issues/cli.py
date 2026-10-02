"""`tracker issues` commands — argument-based; dumps full pydantic models as JSON."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.fields import parse_fields
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues.models import (
    Issue,
    IssueCreate,
    IssueList,
    IssueUpdate,
    count_body,
    filter_body,
)
from ycli.yandex.tracker.typedefs import (
    KeyArg,
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
def get(key: KeyArg, *, tracker: TrackerClient) -> Issue:
    """Print a single issue (full model) for KEY."""
    return tracker.issues.get(key)


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
) -> IssueList:
    """List issues matching the supplied filters (auto-paginated; --all for everything)."""
    body = filter_body(queue=queue, status=status, assignee=assignee, epic=epic, type_=type_)
    return tracker.issues.search(body, limit=config.http.cap(limit, all_=all_))


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="TQL query.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> IssueList:
    """Search issues by a TQL query string (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.issues.search({"query": query}, limit=cap)


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
    return tracker.issues.create(body=named.model_dump(exclude_none=True) | parse_fields(field))


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
    return tracker.issues.update(
        key, body=named.model_dump(exclude_none=True) | parse_fields(field)
    )


@app.command()
def move(
    key: KeyArg,
    queue: Annotated[str, typer.Argument(metavar="QUEUE", help="Target queue key, e.g. NEW.")],
    *,
    tracker: TrackerClient,
) -> Issue:
    """Move issue KEY to another QUEUE (POST /issues/{key}/_move?queue=QUEUE)."""
    return tracker.issues.move(key, queue)


@app.command()
def suggest(
    text: Annotated[str, typer.Argument(metavar="INPUT", help="Text fragment to match in titles.")],
    *,
    tracker: TrackerClient,
) -> IssueList:
    """Suggest issues whose summary contains INPUT (GET /issues/_suggest?input=INPUT)."""
    return tracker.issues.suggest(text)


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
    tracker.issues.scroll_clear(parse_fields(pair))
    return Ack.cleared("search scroll resources")
