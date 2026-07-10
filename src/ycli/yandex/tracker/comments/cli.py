"""`tracker comments` commands."""

from __future__ import annotations

import enum
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.comments.models import CommentUpdate
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
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
def list_(ctx: typer.Context, key: KeyArg) -> None:
    """List comments on issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.tracker.comments.list(key), app_ctx.strategy, app_ctx.console)


@app.command()
def add(
    ctx: typer.Context,
    key: KeyArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
) -> None:
    """Add a comment to issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.comments.add(key, body={"text": text}), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
    key: KeyArg,
    comment_id: CommentIdArg,
    text: Annotated[str, typer.Option(help="New comment text (YFM markdown supported).")],
) -> None:
    """Edit comment COMMENT_ID on issue KEY."""
    body = CommentUpdate(text=text).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.comments.edit(key, comment_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(ctx: typer.Context, key: KeyArg, comment_id: CommentIdArg) -> None:
    """Delete comment COMMENT_ID from issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.comments.delete(key, comment_id)
    print(f"Deleted comment {comment_id} on {key}")


@app.command()
def react(
    ctx: typer.Context,
    key: KeyArg,
    comment_id: CommentIdArg,
    name: Annotated[Reaction, typer.Argument(help="Reaction name, e.g. LIKE, HEART, ROCKET.")],
) -> None:
    """Add reaction NAME to comment COMMENT_ID on issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.comments.react(key, comment_id, name.value),
        app_ctx.strategy,
        app_ctx.console,
    )
