"""`tracker worklog` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.typedefs import (
    ImportCreatedAtOpt,
    ImportCreatedByOpt,
    IssueKeyArg,
)
from ycli.yandex.tracker.worklog.models import (
    ImportWorklog,
    Worklog,
    WorklogCreate,
    WorklogSearch,
    WorklogUpdate,
)

app = typer.Typer(name="worklog", help="Tracker issue worklog.", no_args_is_help=True)

RecordIDArg = Annotated[
    str, typer.Argument(metavar="RECORD_ID", help="Worklog record id to edit/delete.")
]


@app.command("list")
def list_(
    issue_key: IssueKeyArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[Worklog]:
    """List all worklog entries for issue ISSUE_KEY (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.worklog.list(issue_key, limit=cap)


@app.command()
def search(
    created_by: Annotated[
        str | None, typer.Option("--created-by", help="Author login or id.")
    ] = None,
    created_from: Annotated[
        str | None, typer.Option("--created-from", help="Range start, YYYY-MM-DDThh:mm:ss.")
    ] = None,
    created_to: Annotated[
        str | None, typer.Option("--created-to", help="Range end, YYYY-MM-DDThh:mm:ss.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Worklog]:
    """Search org-wide worklog by author and/or time range (POST /worklog/_search)."""
    period = {"from": created_from, "to": created_to}
    given = created_from is not None or created_to is not None
    body = WorklogSearch.model_validate(
        {"createdBy": created_by, "createdAt": period if given else None}
    )
    return tracker.worklog.search(body=body)


@app.command("list-global")
def list_global(
    created_by: Annotated[
        str | None, typer.Option("--created-by", help="Author login or id.")
    ] = None,
    created_from: Annotated[
        str | None, typer.Option("--from", help="Range start, YYYY-MM-DDThh:mm:ss.")
    ] = None,
    created_to: Annotated[
        str | None, typer.Option("--to", help="Range end, YYYY-MM-DDThh:mm:ss.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Worklog]:
    """List org-wide worklog via GET /worklog (createdAt filters need --created-by)."""
    created_at = [
        f"{prefix}:{value}"
        for prefix, value in (("from", created_from), ("to", created_to))
        if value is not None
    ]
    return tracker.worklog.list_global(created_by=created_by, created_at=created_at or None)


@app.command()
def create(
    issue_key: IssueKeyArg,
    duration: Annotated[
        str, typer.Option(help="Time spent, ISO-8601 duration (e.g. PT2H, PT300M, P1DT3H).")
    ],
    start: Annotated[str, typer.Option(help="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")],
    comment: Annotated[
        str | None, typer.Option(help="Optional note saved in the time report.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Worklog:
    """Log time spent on issue ISSUE_KEY (POST /issues/{key}/worklog)."""
    body = WorklogCreate(duration=duration, start=start, comment=comment)
    return tracker.worklog.create(issue_key, body=body)


@app.command()
def update(
    issue_key: IssueKeyArg,
    record_id: RecordIDArg,
    duration: Annotated[str | None, typer.Option(help="New time spent, ISO-8601 duration.")] = None,
    comment: Annotated[str | None, typer.Option(help="New note for the time report.")] = None,
    *,
    tracker: TrackerClient,
) -> Worklog:
    """Edit worklog RECORD_ID on issue ISSUE_KEY — only supplied fields are sent."""
    body = WorklogUpdate(duration=duration, comment=comment)
    return tracker.worklog.update(issue_key, record_id, body=body)


@app.command()
def delete(issue_key: IssueKeyArg, record_id: RecordIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete worklog RECORD_ID from issue ISSUE_KEY."""
    tracker.worklog.delete(issue_key, record_id)
    return Ack.deleted("worklog", record_id, on=issue_key)


@app.command("import")
def import_(
    issue_key: IssueKeyArg,
    duration: Annotated[str, typer.Option(help="Time spent, ISO-8601 duration (e.g. PT1H).")],
    created_at: ImportCreatedAtOpt,
    created_by: ImportCreatedByOpt,
    start: Annotated[str, typer.Option(help="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")],
    comment: Annotated[
        str | None, typer.Option(help="Optional note saved in the time report.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Worklog]:
    """Import a worklog onto issue ISSUE_KEY (POST /issues/{issue_key}/worklogs/_import)."""
    body = ImportWorklog(
        duration=duration,
        createdAt=created_at,
        createdBy=created_by,
        start=start,
        comment=comment,
    )
    return tracker.worklog.import_(issue_key, body=body)
