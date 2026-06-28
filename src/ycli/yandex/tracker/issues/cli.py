"""`tracker issues` commands — argument-based; dumps full pydantic models as JSON."""
from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from ycli.cliformat import output_format
from ycli.output import render

from ycli.yandex.tracker._clideps import parse_fields, tracker_client

app = typer.Typer(name="issues", help="Tracker issues.", no_args_is_help=True)

KeyArg = Annotated[str, typer.Argument(metavar="KEY", help="Issue key, e.g. DATAENGINEERING-1.")]
FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Extra field key=value (JSON-coerced; repeatable)."),
]


@app.command()
def get(ctx: typer.Context, key: KeyArg) -> None:
    """Print a single issue (full model) for KEY."""
    render(tracker_client(ctx).issues.get(key), output_format=output_format(ctx))


@app.command()
def full(ctx: typer.Context, key: KeyArg) -> None:
    """Print the raw API dict for KEY (no pydantic projection)."""
    print(json.dumps(tracker_client(ctx).issues.get_raw(key), ensure_ascii=False))


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
            "queue": queue, "status": status, "assignee": assignee, "epic": epic, "type": type_,
        }.items()
        if v
    }
    render(tracker_client(ctx).issues.search(body={"filter": flt}), output_format=output_format(ctx))


@app.command()
def search(ctx: typer.Context, query: Annotated[str, typer.Argument(help="TQL query.")]) -> None:
    """Search issues by a TQL query string."""
    render(tracker_client(ctx).issues.search(body={"query": query}), output_format=output_format(ctx))


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
    if query:
        body: dict[str, Any] = {"query": query}
    else:
        body = {"filter": {k: v for k, v in (("queue", queue), ("status", status)) if v}}
    print(tracker_client(ctx).issues.count(body=body))


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
    render(tracker_client(ctx).issues.create(body=body), output_format=output_format(ctx))


@app.command()
def update(
    ctx: typer.Context,
    key: KeyArg,
    summary: Annotated[str, typer.Option(help="New summary.")] = "",
    type_: Annotated[str, typer.Option("--type", help="New issue type key.")] = "",
    priority: Annotated[str, typer.Option(help="New priority key.")] = "",
    parent: Annotated[str, typer.Option(help="New parent issue key.")] = "",
    description: Annotated[str, typer.Option(help='New markdown body — pass "$(cat file.md)".')] = "",
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
    render(tracker_client(ctx).issues.update(key, body=body), output_format=output_format(ctx))
