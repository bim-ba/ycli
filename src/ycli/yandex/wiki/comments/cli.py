"""`wiki comments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.comments.models import (
    CommentCreate,
    CommentCreated,
    CommentDeleteResult,
    CommentList,
)

app = typer.Typer(name="comments", help="Wiki page comments.", no_args_is_help=True)

PageIdArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]


@app.command("list")
def list_(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> CommentList:
    """List comments on a page id (GET /pages/{id}/comments; auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.comments.list(page_id=page_id, limit=cap)


@app.command()
def thread(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Root comment id.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> CommentList:
    """Print the thread for COMMENT_ID on PAGE_ID: the comment plus its replies.

    Reconstructed from the page's comment list (the Wiki /thread endpoint, see `thread-get`, is
    dead); the comment comes first, then its descendants chained by parent_id.
    """
    cap = config.http.cap(limit, all_=all_)
    return wiki.comments.thread(page_id=page_id, comment_id=comment_id, limit=cap)


@app.command("thread-get")
def thread_get(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Root comment id.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> CommentList:
    """Print what the server returns as the thread of COMMENT_ID (GET .../comments/{id}/thread).

    The server answers an empty list for every real thread (checked 2026-10-02); use `thread`,
    which rebuilds it from the comment list.
    """
    cap = resolve_cap(limit, config.http.max_items, all_=all_)
    return wiki.comments.thread_get(page_id=page_id, comment_id=comment_id, limit=cap)


@app.command()
def create(
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
    *,
    wiki: WikiClient,
) -> CommentCreated:
    """Add a comment to a page (POST /pages/{id}/comments)."""
    payload = CommentCreate(
        body=body,
        inline_text=inline_text or None,
        parent_id=parent_id or None,
        thread_id=thread_id or None,
    )
    return wiki.comments.create(page_id=page_id, body=payload.model_dump(exclude_none=True))


@app.command()
def delete(
    page_id: PageIdArg,
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Comment id to delete.")],
    *,
    wiki: WikiClient,
) -> CommentDeleteResult:
    """Delete a comment (DELETE /pages/{id}/comments/{comment_id}); emits the remaining count."""
    return wiki.comments.delete(page_id=page_id, comment_id=comment_id)
