"""`tracker import` commands — admin-only data import (preserves source history)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment
from ycli.yandex.tracker.import_.models import (
    ImportComment,
    ImportLink,
    ImportTask,
    ImportWorklog,
)
from ycli.yandex.tracker.issues.models import Issue
from ycli.yandex.tracker.links.models import Link
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)
from ycli.yandex.tracker.worklog.models import Worklog

app = typer.Typer(name="import", help="Tracker data import (admin).", no_args_is_help=True)

CreatedAtOpt = Annotated[
    str, typer.Option("--created-at", help="Original creation time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
]
CreatedByOpt = Annotated[
    str, typer.Option("--created-by", help="Login or id of the original author.")
]


@app.command()
def task(
    queue: Annotated[str, typer.Option(help="Target queue key.")],
    summary: Annotated[str, typer.Option(help="Issue title.")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
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
    return tracker.import_.task(body=body)


@app.command()
def comment(
    key: KeyArg,
    text: Annotated[str, typer.Option(help="Comment text.")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    *,
    tracker: TrackerClient,
) -> Comment:
    """Import a comment onto issue KEY (POST /issues/{key}/comments/_import)."""
    body = ImportComment(text=text, createdAt=created_at, createdBy=created_by)
    return tracker.import_.comment(key, body=body)


@app.command()
def link(
    key: KeyArg,
    relationship: Annotated[str, typer.Option(help="Link type, e.g. relates.")],
    issue: Annotated[str, typer.Option(help="Key or id of the issue to link to.")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    *,
    tracker: TrackerClient,
) -> Link:
    """Import a link on issue KEY (POST /issues/{key}/links/_import)."""
    body = ImportLink(
        relationship=relationship, issue=issue, createdAt=created_at, createdBy=created_by
    )
    return tracker.import_.link(key, body=body)


@app.command()
def worklog(
    key: KeyArg,
    duration: Annotated[str, typer.Option(help="Time spent, ISO-8601 duration (e.g. PT1H).")],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    start: Annotated[str, typer.Option(help="Work start time, YYYY-MM-DDThh:mm:ss.sss±hhmm.")],
    comment: Annotated[
        str | None, typer.Option(help="Optional note saved in the time report.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Worklog]:
    """Import a worklog onto issue KEY (POST /issues/{key}/worklogs/_import)."""
    body = ImportWorklog(
        duration=duration,
        createdAt=created_at,
        createdBy=created_by,
        start=start,
        comment=comment,
    )
    return tracker.import_.worklog(key, body=body)


@app.command()
def file(
    key: KeyArg,
    path: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, readable=True, help="Local file to attach."),
    ],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    filename: Annotated[
        str | None, typer.Option(help="Override the attachment name (default: basename).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Attachment:
    """Import a file attachment onto issue KEY (POST /issues/{key}/attachments/_import)."""
    return tracker.import_.file(
        key,
        filename=path.name if filename is None else filename,
        created_at=created_at,
        created_by=created_by,
        data=path.read_bytes(),
    )


@app.command("comment-file")
def comment_file(
    key: KeyArg,
    comment_id: Annotated[str, typer.Argument(metavar="COMMENT_ID", help="Id of the comment.")],
    path: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, readable=True, help="Local file to attach."),
    ],
    created_at: CreatedAtOpt,
    created_by: CreatedByOpt,
    filename: Annotated[
        str | None, typer.Option(help="Override the attachment name (default: basename).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Attachment:
    """Import a file onto comment COMMENT_ID of issue KEY (…/comments/{id}/attachments/_import)."""
    return tracker.import_.comment_file(
        key,
        comment_id,
        filename=path.name if filename is None else filename,
        created_at=created_at,
        created_by=created_by,
        data=path.read_bytes(),
    )
