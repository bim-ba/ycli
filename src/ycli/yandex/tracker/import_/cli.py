"""`tracker import` commands — admin-only data import (preserves source history)."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003  # used at runtime (read_bytes) + typer arg annotation
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.import_.models import (
    ImportComment,
    ImportLink,
    ImportTask,
    ImportWorklog,
)
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="import", help="Tracker data import (admin).", no_args_is_help=True)

CreatedAtOpt = Annotated[
    str, typer.Option("--created-at", help="Original creation time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
]
CreatedByOpt = Annotated[
    str, typer.Option("--created-by", help="Login or id of the original author.")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def task(
    ctx: typer.Context,
    queue: Annotated[str, typer.Option(help="Target queue key.")],
    summary: Annotated[str, typer.Option(help="Issue title.")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    key: Annotated[str, typer.Option(help="Explicit issue key (must belong to the queue).")] = "",
    description: Annotated[str, typer.Option(help="Issue description (YFM).")] = "",
    assignee: Annotated[str, typer.Option(help="Assignee login or id.")] = "",
) -> None:
    """Import an issue preserving its history (POST /issues/_import)."""
    body = ImportTask(
        queue=queue,
        summary=summary,
        createdAt=created_at,
        createdBy=created_by,
        key=key or None,
        description=description or None,
        assignee=assignee or None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.import_.task(body=body), app_ctx.strategy, app_ctx.console)


@app.command()
def comment(
    ctx: typer.Context,
    key: KeyArg,
    text: Annotated[str, typer.Option(help="Comment text.")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
) -> None:
    """Import a comment onto issue KEY (POST /issues/{key}/comments/_import)."""
    body = ImportComment(text=text, createdAt=created_at, createdBy=created_by).model_dump(
        by_alias=True, exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.import_.comment(key, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def link(
    ctx: typer.Context,
    key: KeyArg,
    relationship: Annotated[str, typer.Option(help="Link type, e.g. relates.")],
    issue: Annotated[str, typer.Option(help="Key or id of the issue to link to.")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
) -> None:
    """Import a link on issue KEY (POST /issues/{key}/links/_import)."""
    body = ImportLink(
        relationship=relationship, issue=issue, createdAt=created_at, createdBy=created_by
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.import_.link(key, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def worklog(
    ctx: typer.Context,
    key: KeyArg,
    duration: Annotated[str, typer.Option(help="Time spent, ISO-8601 duration (e.g. PT1H).")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    start: Annotated[str, typer.Option(help="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")],
    comment: Annotated[str, typer.Option(help="Optional note saved in the time report.")] = "",
) -> None:
    """Import a worklog onto issue KEY (POST /issues/{key}/worklogs/_import)."""
    body = ImportWorklog(
        duration=duration,
        createdAt=created_at,
        createdBy=created_by,
        start=start,
        comment=comment or None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.import_.worklog(key, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def file(
    ctx: typer.Context,
    key: KeyArg,
    path: Annotated[Path, typer.Argument(help="Local file to attach.")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    filename: Annotated[
        str, typer.Option(help="Override the attachment name (default: basename).")
    ] = "",
) -> None:
    """Import a file attachment onto issue KEY (POST /issues/{key}/attachments/_import)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.import_.file(
            key,
            filename=filename or path.name,
            created_at=created_at,
            created_by=created_by,
            data=path.read_bytes(),
        ),
        app_ctx.strategy,
        app_ctx.console,
    )
