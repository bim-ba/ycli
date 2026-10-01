"""`tracker worklog` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)
from ycli.yandex.tracker.worklog.models import Worklog, WorklogCreate, WorklogList, WorklogUpdate

app = typer.Typer(name="worklog", help="Tracker issue worklog.", no_args_is_help=True)

RecordIdArg = Annotated[
    str, typer.Argument(metavar="RECORD_ID", help="Worklog record id to edit/delete.")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    key: KeyArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> WorklogList:
    """List all worklog entries for issue KEY (auto-paginated; --all for everything)."""
    cap = resolve_cap(limit, config.http.max_items, all_=all_)
    return tracker.worklog.list(key, limit=cap)


@app.command()
def search(
    created_by: Annotated[str, typer.Option("--created-by", help="Author login or id.")] = "",
    created_from: Annotated[
        str, typer.Option("--from", help="Range start, YYYY-MM-DDThh:mm:ss.")
    ] = "",
    created_to: Annotated[str, typer.Option("--to", help="Range end, YYYY-MM-DDThh:mm:ss.")] = "",
    *,
    tracker: TrackerClient,
) -> WorklogList:
    """Search org-wide worklog by author and/or time range (POST /worklog/_search)."""
    body: dict[str, object] = {}
    if created_by:
        body["createdBy"] = created_by
    created_at = {k: v for k, v in (("from", created_from), ("to", created_to)) if v}
    if created_at:
        body["createdAt"] = created_at
    return tracker.worklog.search(body=body)


@app.command("global-list")
def global_list(
    created_by: Annotated[str, typer.Option("--created-by", help="Author login or id.")] = "",
    created_from: Annotated[
        str, typer.Option("--from", help="Range start, YYYY-MM-DDThh:mm:ss.")
    ] = "",
    created_to: Annotated[str, typer.Option("--to", help="Range end, YYYY-MM-DDThh:mm:ss.")] = "",
    *,
    tracker: TrackerClient,
) -> WorklogList:
    """List org-wide worklog via GET /worklog (createdAt filters need --created-by)."""
    created_at = [
        f"{prefix}:{value}"
        for prefix, value in (("from", created_from), ("to", created_to))
        if value
    ]
    return tracker.worklog.global_list(created_by=created_by or None, created_at=created_at or None)


@app.command()
def add(
    key: KeyArg,
    duration: Annotated[
        str, typer.Option(help="Time spent, ISO-8601 duration (e.g. PT2H, PT300M, P1DT3H).")
    ],
    start: Annotated[str, typer.Option(help="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")] = "",
    comment: Annotated[str, typer.Option(help="Optional note saved in the time report.")] = "",
    *,
    tracker: TrackerClient,
) -> Worklog:
    """Log time spent on issue KEY (POST /issues/{key}/worklog)."""
    body = WorklogCreate(
        duration=duration, start=start or None, comment=comment or None
    ).model_dump(exclude_none=True)
    return tracker.worklog.create(key, body=body)


@app.command()
def edit(
    key: KeyArg,
    record_id: RecordIdArg,
    duration: Annotated[str, typer.Option(help="New time spent, ISO-8601 duration.")] = "",
    comment: Annotated[str, typer.Option(help="New note for the time report.")] = "",
    *,
    tracker: TrackerClient,
) -> Worklog:
    """Edit worklog RECORD_ID on issue KEY — only supplied fields are sent."""
    body = WorklogUpdate(duration=duration or None, comment=comment or None).model_dump(
        exclude_none=True
    )
    return tracker.worklog.edit(key, record_id, body=body)


@app.command()
def delete(key: KeyArg, record_id: RecordIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete worklog RECORD_ID from issue KEY."""
    tracker.worklog.delete(key, record_id)
    return Ack.deleted("worklog", record_id, on=key)
