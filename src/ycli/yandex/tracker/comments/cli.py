"""`tracker comments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_argument
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment, CommentUpdate, ImportComment, Reaction
from ycli.yandex.tracker.models import CommentCreate
from ycli.yandex.tracker.typedefs import (
    ExpandOpt,
    ImportCreatedAtOpt,
    ImportCreatedByOpt,
    IssueKeyArg,
)

app = typer.Typer(name="comments", help="Tracker issue comments.", no_args_is_help=True)

IssueCommentIDArg = Annotated[
    str, typer.Argument(metavar="COMMENT_ID", help="Comment id (numeric id or longId).")
]


@app.command("list")
def list_(
    issue_key: IssueKeyArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    expand: ExpandOpt = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[Comment]:
    """List all comments on issue ISSUE_KEY (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.comments.list(issue_key, limit=cap, expand=expand)


@app.command()
def get(
    issue_key: IssueKeyArg,
    comment_id: IssueCommentIDArg,
    expand: Annotated[
        str | None, typer.Option(help="Extra fields: attachments, html or all (comma-separated).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Comment:
    """Print comment COMMENT_ID of issue ISSUE_KEY."""
    return tracker.comments.get(issue_key, comment_id, expand=expand)


@app.command()
def create(
    issue_key: IssueKeyArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
    *,
    tracker: TrackerClient,
) -> Comment:
    """Add a comment to issue ISSUE_KEY."""
    body = CommentCreate(text=text)
    return tracker.comments.create(issue_key, body=body)


@app.command()
def update(
    issue_key: IssueKeyArg,
    comment_id: IssueCommentIDArg,
    text: Annotated[str, typer.Option(help="New comment text (YFM markdown supported).")],
    *,
    tracker: TrackerClient,
) -> Comment:
    """Edit comment COMMENT_ID on issue ISSUE_KEY."""
    body = CommentUpdate(text=text)
    return tracker.comments.update(issue_key, comment_id, body=body)


@app.command()
def delete(issue_key: IssueKeyArg, comment_id: IssueCommentIDArg, *, tracker: TrackerClient) -> Ack:
    """Delete comment COMMENT_ID from issue ISSUE_KEY."""
    tracker.comments.delete(issue_key, comment_id)
    return Ack.deleted("comment", comment_id, on=issue_key)


@app.command()
def reactions_create(
    issue_key: IssueKeyArg,
    comment_id: IssueCommentIDArg,
    name: Annotated[str, values_argument(Reaction, help="Reaction name.")],
    *,
    tracker: TrackerClient,
) -> Comment:
    """Add reaction NAME to comment COMMENT_ID on issue ISSUE_KEY."""
    return tracker.comments.reactions_create(issue_key, comment_id, name)


@app.command("import")
def import_(
    issue_key: IssueKeyArg,
    text: Annotated[str, typer.Option(help="Comment text.")],
    created_at: ImportCreatedAtOpt,
    created_by: ImportCreatedByOpt,
    *,
    tracker: TrackerClient,
) -> Comment:
    """Import a comment onto issue ISSUE_KEY (POST /issues/{issue_key}/comments/_import)."""
    body = ImportComment(text=text, createdAt=created_at, createdBy=created_by)
    return tracker.comments.import_(issue_key, body=body)
