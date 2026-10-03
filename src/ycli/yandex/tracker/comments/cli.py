"""`tracker comments` commands."""

from __future__ import annotations

import enum
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.comments.models import Comment, CommentUpdate
from ycli.yandex.tracker.models import CommentCreate
from ycli.yandex.tracker.typedefs import (
    ExpandOpt,
    KeyArg,
)

app = typer.Typer(name="comments", help="Tracker issue comments.", no_args_is_help=True)

CommentIdArg = Annotated[
    str, typer.Argument(metavar="COMMENT_ID", help="Comment id (numeric id or longId).")
]


class Reaction(enum.StrEnum):
    """Reaction names accepted by ``POST …/comments/{id}/reactions/{name}``."""

    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    LAUGH = "LAUGH"
    HOORAY = "HOORAY"
    CONFUSED = "CONFUSED"
    HEART = "HEART"
    ROCKET = "ROCKET"
    EYES = "EYES"
    FIRE = "FIRE"
    OK = "OK"
    FACEPALM = "FACEPALM"
    CHECK = "CHECK"


@app.command("list")
def list_(
    key: KeyArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    expand: ExpandOpt = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[Comment]:
    """List all comments on issue KEY (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.comments.list(key, limit=cap, expand=expand)


@app.command()
def get(
    key: KeyArg,
    comment_id: CommentIdArg,
    expand: Annotated[
        str | None, typer.Option(help="Extra fields: attachments, html or all (comma-separated).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Comment:
    """Print comment COMMENT_ID of issue KEY."""
    return tracker.comments.get(key, comment_id, expand=expand)


@app.command()
def add(
    key: KeyArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
    *,
    tracker: TrackerClient,
) -> Comment:
    """Add a comment to issue KEY."""
    body = CommentCreate(text=text)
    return tracker.comments.add(key, body=body)


@app.command()
def update(
    key: KeyArg,
    comment_id: CommentIdArg,
    text: Annotated[str, typer.Option(help="New comment text (YFM markdown supported).")],
    *,
    tracker: TrackerClient,
) -> Comment:
    """Edit comment COMMENT_ID on issue KEY."""
    body = CommentUpdate(text=text)
    return tracker.comments.update(key, comment_id, body=body)


@app.command()
def delete(key: KeyArg, comment_id: CommentIdArg, *, tracker: TrackerClient) -> Ack:
    """Delete comment COMMENT_ID from issue KEY."""
    tracker.comments.delete(key, comment_id)
    return Ack.deleted("comment", comment_id, on=key)


@app.command()
def react(
    key: KeyArg,
    comment_id: CommentIdArg,
    name: Annotated[Reaction, typer.Argument(help="Reaction name, e.g. LIKE, HEART, ROCKET.")],
    *,
    tracker: TrackerClient,
) -> Comment:
    """Add reaction NAME to comment COMMENT_ID on issue KEY."""
    return tracker.comments.react(key, comment_id, name.value)
