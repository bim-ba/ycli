"""`tracker issues` commands — argument-based; dumps full pydantic models as JSON."""

from __future__ import annotations

from typing import Annotated, Any

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)
from ycli.yandex.tracker.utils import count_body, parse_fields

app = typer.Typer(name="issues", help="Tracker issues.", no_args_is_help=True)

FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Extra field key=value (JSON-coerced; repeatable)."),
]


@app.command()
def get(ctx: typer.Context, key: KeyArg) -> None:
    """Print a single issue (full model) for KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.issues.get(key), app_ctx.strategy, app_ctx.console)


@app.command("list")
def list_(
    ctx: typer.Context,
    queue: Annotated[str, typer.Option(help="Queue key.")] = "",
    status: Annotated[str, typer.Option(help="Status key.")] = "",
    assignee: Annotated[str, typer.Option(help="Assignee login.")] = "",
    epic: Annotated[str, typer.Option(help="Epic key.")] = "",
    type_: Annotated[str, typer.Option("--type", help="Issue type key.")] = "",
) -> None:
    """List issues matching the supplied filters (omitted filters dropped)."""
    flt = {
        k: v
        for k, v in {
            "queue": queue,
            "status": status,
            "assignee": assignee,
            "epic": epic,
            "type": type_,
        }.items()
        if v
    }
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.issues.search(body={"filter": flt}), app_ctx.strategy, app_ctx.console
    )


@app.command()
def search(ctx: typer.Context, query: Annotated[str, typer.Argument(help="TQL query.")]) -> None:
    """Search issues by a TQL query string."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.issues.search(body={"query": query}), app_ctx.strategy, app_ctx.console
    )


@app.command()
def count(
    ctx: typer.Context,
    query: Annotated[str, typer.Option(help="TQL query (mutually exclusive with filters).")] = "",
    queue: Annotated[str, typer.Option(help="Queue key.")] = "",
    status: Annotated[str, typer.Option(help="Status key.")] = "",
) -> None:
    """Count issues matching a TQL query or filters (bare integer).

    With no ``--query`` and no filters this sends an empty filter — the API then counts
    EVERY issue in the org. Pass ``--queue``/``--status`` (or ``--query``) to narrow.
    """
    app_ctx = AppContext.from_typer_context(ctx)
    print(app_ctx.tracker.issues.count(body=count_body(query=query, queue=queue, status=status)))


@app.command()
def create(
    ctx: typer.Context,
    queue: Annotated[str, typer.Option(help="Target queue key.")],
    summary: Annotated[str, typer.Option(help="Issue summary (title).")],
    type_: Annotated[str, typer.Option("--type", help="Issue type key, e.g. task.")] = "",
    priority: Annotated[str, typer.Option(help="Priority key, e.g. normal.")] = "",
    parent: Annotated[str, typer.Option(help="Parent issue key.")] = "",
    description: Annotated[str, typer.Option(help='Markdown body — pass "$(cat file.md)".')] = "",
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    field: FieldOpt = None,
) -> None:
    """Create an issue (POST /issues/). type/priority wrap to {"key": …}; queue/parent stay bare."""
    body: dict[str, Any] = {"queue": queue, "summary": summary}
    if type_:
        body["type"] = {"key": type_}
    if priority:
        body["priority"] = {"key": priority}
    if parent:
        body["parent"] = parent
    if description:
        body["description"] = description
    if tag:
        body["tags"] = tag
    body |= parse_fields(field)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.issues.create(body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def update(
    ctx: typer.Context,
    key: KeyArg,
    summary: Annotated[str, typer.Option(help="New summary.")] = "",
    type_: Annotated[str, typer.Option("--type", help="New issue type key.")] = "",
    priority: Annotated[str, typer.Option(help="New priority key.")] = "",
    parent: Annotated[str, typer.Option(help="New parent issue key.")] = "",
    description: Annotated[
        str, typer.Option(help='New markdown body — pass "$(cat file.md)".')
    ] = "",
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    field: FieldOpt = None,
) -> None:
    """Update issue KEY (PATCH /issues/{key}) — only supplied fields are sent."""
    body: dict[str, Any] = {}
    if summary:
        body["summary"] = summary
    if type_:
        body["type"] = {"key": type_}
    if priority:
        body["priority"] = {"key": priority}
    if parent:
        body["parent"] = parent
    if description:
        body["description"] = description
    if tag:
        body["tags"] = tag
    body |= parse_fields(field)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.issues.update(key, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def move(
    ctx: typer.Context,
    key: KeyArg,
    queue: Annotated[str, typer.Argument(metavar="QUEUE", help="Target queue key, e.g. NEW.")],
) -> None:
    """Move issue KEY to another QUEUE (POST /issues/{key}/_move?queue=QUEUE)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.issues.move(key, queue), app_ctx.strategy, app_ctx.console)


@app.command()
def suggest(
    ctx: typer.Context,
    text: Annotated[str, typer.Argument(metavar="INPUT", help="Text fragment to match in titles.")],
) -> None:
    """Suggest issues whose summary contains INPUT (GET /issues/_suggest?input=INPUT)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.issues.suggest(text), app_ctx.strategy, app_ctx.console)


@app.command("scroll-clear")
def scroll_clear(
    ctx: typer.Context,
    pair: Annotated[
        list[str] | None,
        typer.Option("--pair", help="scrollId=scrollToken pair to release (repeatable)."),
    ] = None,
) -> None:
    """Release search-scroll resources (POST /system/search/scroll/_clear).

    Pass each ``--pair scrollId=scrollToken`` from a scrolled ``issues search``.
    """
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.issues.scroll_clear(parse_fields(pair))
    print("Cleared search scroll resources")
