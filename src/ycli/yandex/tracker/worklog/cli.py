"""`tracker worklog` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)
from ycli.yandex.tracker.worklog.models import WorklogCreate, WorklogUpdate

app = typer.Typer(name="worklog", help="Tracker issue worklog.", no_args_is_help=True)

RecordIdArg = Annotated[
    str, typer.Argument(metavar="RECORD_ID", help="Worklog record id to edit/delete.")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    key: KeyArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
) -> None:
    """List all worklog entries for issue KEY (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(
        app_ctx.tracker.worklog.list(key, limit=cap), app_ctx.strategy, app_ctx.console
    )


@app.command()
def search(
    ctx: typer.Context,
    created_by: Annotated[str, typer.Option("--created-by", help="Author login or id.")] = "",
    created_from: Annotated[
        str, typer.Option("--from", help="Range start, YYYY-MM-DDThh:mm:ss.")
    ] = "",
    created_to: Annotated[str, typer.Option("--to", help="Range end, YYYY-MM-DDThh:mm:ss.")] = "",
) -> None:
    """Search org-wide worklog by author and/or time range (POST /worklog/_search)."""
    body: dict[str, object] = {}
    if created_by:
        body["createdBy"] = created_by
    created_at = {k: v for k, v in (("from", created_from), ("to", created_to)) if v}
    if created_at:
        body["createdAt"] = created_at
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.worklog.search(body=body), app_ctx.strategy, app_ctx.console
    )


@app.command("global-list")
def global_list(
    ctx: typer.Context,
    created_by: Annotated[str, typer.Option("--created-by", help="Author login or id.")] = "",
    created_from: Annotated[
        str, typer.Option("--from", help="Range start, YYYY-MM-DDThh:mm:ss.")
    ] = "",
    created_to: Annotated[str, typer.Option("--to", help="Range end, YYYY-MM-DDThh:mm:ss.")] = "",
) -> None:
    """List org-wide worklog via GET /worklog (createdAt filters need --created-by)."""
    created_at = [
        f"{prefix}:{value}"
        for prefix, value in (("from", created_from), ("to", created_to))
        if value
    ]
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.worklog.global_list(
            created_by=created_by or None, created_at=created_at or None
        ),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    duration: Annotated[
        str, typer.Option(help="Time spent, ISO-8601 duration (e.g. PT2H, PT300M, P1DT3H).")
    ],
    start: Annotated[str, typer.Option(help="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")] = "",
    comment: Annotated[str, typer.Option(help="Optional note saved in the time report.")] = "",
) -> None:
    """Log time spent on issue KEY (POST /issues/{key}/worklog)."""
    body = WorklogCreate(
        duration=duration, start=start or None, comment=comment or None
    ).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.worklog.create(key, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
    key: KeyArg,
    record_id: RecordIdArg,
    duration: Annotated[str, typer.Option(help="New time spent, ISO-8601 duration.")] = "",
    comment: Annotated[str, typer.Option(help="New note for the time report.")] = "",
) -> None:
    """Edit worklog RECORD_ID on issue KEY — only supplied fields are sent."""
    body = WorklogUpdate(duration=duration or None, comment=comment or None).model_dump(
        exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.worklog.edit(key, record_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(ctx: typer.Context, key: KeyArg, record_id: RecordIdArg) -> None:
    """Delete worklog RECORD_ID from issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.worklog.delete(key, record_id)
    Serializer.serialize(
        Ack.deleted("worklog", record_id, on=key), app_ctx.strategy, app_ctx.console
    )
