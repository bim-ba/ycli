"""`wiki comments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.wiki.comments.models import CommentCreate

app = typer.Typer(name="comments", help="Wiki page comments.", no_args_is_help=True)

PageIdArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]


@app.command("list")
def list_(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: Annotated[int, typer.Option(help="Max comments (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every comment (no cap).")] = False,
) -> None:
    """List comments on a page id (GET /pages/{id}/comments; auto-paginated)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.wiki.comments.list(page_id=page_id, limit=cap), app_ctx.strategy, app_ctx.console
    )


@app.command()
def thread(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Root comment id.")],
    limit: Annotated[int, typer.Option(help="Max replies (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every reply (no cap).")] = False,
) -> None:
    """Print the reply thread rooted at COMMENT_ID on PAGE_ID (auto-paginated)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.wiki.comments.thread(page_id=page_id, comment_id=comment_id, limit=cap),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def create(
    ctx: typer.Context,
    page_id: PageIdArg,
    body: Annotated[str, typer.Option(help="Comment text.")],
    inline_text: Annotated[
        str, typer.Option("--inline-text", help="Page fragment to pin the comment to.")
    ] = "",
    parent_id: Annotated[
        int, typer.Option("--parent-id", help="Reply to this comment id (threaded).")
    ] = 0,
    thread_id: Annotated[
        int, typer.Option("--thread-id", help="File into this existing thread id.")
    ] = 0,
) -> None:
    """Add a comment to a page (POST /pages/{id}/comments)."""
    app_ctx = AppContext.from_typer_context(ctx)
    payload = CommentCreate(
        body=body,
        inline_text=inline_text or None,
        parent_id=parent_id or None,
        thread_id=thread_id or None,
    )
    Serializer.serialize(
        app_ctx.wiki.comments.create(page_id=page_id, body=payload.model_dump(exclude_none=True)),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(
    ctx: typer.Context,
    page_id: PageIdArg,
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Comment id to delete.")],
) -> None:
    """Delete a comment (DELETE /pages/{id}/comments/{comment_id}); emits the remaining count."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.comments.delete(page_id=page_id, comment_id=comment_id),
        app_ctx.strategy,
        app_ctx.console,
    )
