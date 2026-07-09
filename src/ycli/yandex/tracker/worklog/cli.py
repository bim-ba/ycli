"""`tracker worklog` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
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
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List worklog entries for issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.worklog.list(key), app_ctx.strategy, app_ctx.console)


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
    print(f"Deleted worklog {record_id} on {key}")
