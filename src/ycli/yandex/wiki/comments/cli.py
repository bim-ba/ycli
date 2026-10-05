"""`wiki comments` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList, SortDirection
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.comments.models import (
    Comment,
    CommentCreate,
    CommentCreated,
    CommentDeleteResult,
)
from ycli.yandex.wiki.models import ResolveStatus
from ycli.yandex.wiki.typedefs import PageIDArg

app = typer.Typer(name="comments", help="Wiki page comments.", no_args_is_help=True)


@app.command("list")
def list_(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: LimitOption = None,
    all_: AllOption = False,
    order_by: Annotated[
        str | None, typer.Option("--order-by", help="Sort field: created_at.")
    ] = None,
    order_direction: Annotated[
        str | None,
        values_option(SortDirection, "--order-direction", help="Sort direction for --order-by."),
    ] = None,
    status_filter: Annotated[
        str | None,
        values_option(ResolveStatus, "--status-filter", help="Only comments in this state."),
    ] = None,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[Comment]:
    """List comments on a page id (GET /pages/{id}/comments; auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.comments.list(
        page_id=page_id,
        limit=cap,
        order_by=order_by,
        order_direction=order_direction,
        status_filter=status_filter,
    )


@app.command()
def thread_list(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Root comment id.")],
    limit: LimitOption = None,
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
    return wiki.comments.thread_list(page_id=page_id, comment_id=comment_id, limit=cap)


@app.command("thread-get")
def thread_get(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Root comment id.")],
    limit: LimitOption = None,
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
    page_id: PageIDArg,
    body: Annotated[str, typer.Option(help="Comment text.")],
    inline_text: Annotated[
        str | None, typer.Option("--inline-text", help="Page fragment to pin the comment to.")
    ] = None,
    parent_id: Annotated[
        int | None, typer.Option("--parent-id", help="Reply to this comment id (threaded).")
    ] = None,
    thread_id: Annotated[
        int | None, typer.Option("--thread-id", help="File into this existing thread id.")
    ] = None,
    *,
    wiki: WikiClient,
) -> CommentCreated:
    """Add a comment to a page (POST /pages/{id}/comments)."""
    payload = CommentCreate(
        body=body,
        inline_text=inline_text,
        parent_id=parent_id,
        thread_id=thread_id,
    )
    return wiki.comments.create(page_id=page_id, body=payload)


@app.command()
def delete(
    page_id: PageIDArg,
    comment_id: Annotated[int, typer.Argument(metavar="COMMENT_ID", help="Comment id to delete.")],
    *,
    wiki: WikiClient,
) -> CommentDeleteResult:
    """Delete a comment (DELETE /pages/{id}/comments/{comment_id}); emits the remaining count."""
    return wiki.comments.delete(page_id=page_id, comment_id=comment_id)
