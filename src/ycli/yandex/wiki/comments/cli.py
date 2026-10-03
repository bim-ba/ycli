"""`wiki comments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.comments.models import (
    Comment,
    CommentCreate,
    CommentCreated,
    CommentDeleteResult,
)

app = typer.Typer(name="comments", help="Wiki page comments.", no_args_is_help=True)

PageIdArg = Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")]


@app.command("list")
def list_(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    order_by: Annotated[str, typer.Option("--order-by", help="Sort field: created_at.")] = "",
    order_direction: Annotated[
        str, typer.Option("--order-direction", help="Sort direction for --order-by: asc or desc.")
    ] = "",
    status: Annotated[
        str, typer.Option("--status", help="Only resolved or only unresolved comments.")
    ] = "",
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[Comment]:
    """List comments on a page id (GET /pages/{id}/comments; auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.comments.list(
        page_id=page_id,
        limit=cap,
        order_by=order_by or None,
        order_direction=order_direction or None,
        status_filter=status or None,
    )


@app.command()
def thread_list(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Root comment id.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[Comment]:
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
) -> ItemList[Comment]:
    """Print what the server returns as the thread of COMMENT_ID (GET .../comments/{id}/thread).

    The server answers an empty list for every real thread (checked 2026-10-02); use `thread-list`,
    which rebuilds it from the comment list.
    """
    cap = config.http.cap(limit, all_=all_)
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
    return wiki.comments.create(page_id=page_id, body=payload)


@app.command()
def delete(
    page_id: PageIdArg,
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Comment id to delete.")],
    *,
    wiki: WikiClient,
) -> CommentDeleteResult:
    """Delete a comment (DELETE /pages/{id}/comments/{comment_id}); emits the remaining count."""
    return wiki.comments.delete(page_id=page_id, comment_id=comment_id)
