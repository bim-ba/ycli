"""Wiki /pages/{id}/comments FastMCP tools."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import ItemList, SortDirection
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.comments.models import (
    Comment,
    CommentCreate,
    CommentCreated,
    CommentDeleteResult,
)
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    PageID,
    app_config,
    new_server,
    wiki_client,
)
from ycli.yandex.wiki.models import ResolveStatus

mcp = new_server("wiki-comments")


@mcp.tool(name="comments_list", annotations={**RO, "title": "List Wiki comments"})
def list_(
    page_id: PageID,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max comments to return; {LIMIT_CAP}")
    ] = None,
    order_by: Annotated[str | None, Field(description="Sort field: ``created_at``.")] = None,
    order_direction: Annotated[
        SortDirection | None, Field(description="Sort direction for ``order_by``.")
    ] = None,
    status_filter: Annotated[
        ResolveStatus | None, Field(description="Keep only the comments in this state.")
    ] = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Comment]:
    """Comments on a page id, auto-paginated (drains the ``next_cursor`` internally).

    Capped at the configured item cap unless ``limit`` is given. Pair with
    ``pages_get_meta`` (its ``attributes.comments_count`` tells you how many exist).
    """
    cap = config.http.cap(limit)
    return client.comments.list(
        page_id=page_id,
        limit=cap,
        order_by=order_by,
        order_direction=order_direction,
        status_filter=status_filter,
    )


@mcp.tool(name="comments_thread_list", annotations={**RO, "title": "List Wiki comment thread"})
def thread_list(
    page_id: Annotated[int, Field(description="Numeric page id the comment lives on.")],
    comment_id: Annotated[int, Field(description="Root comment id whose reply thread to fetch.")],
    limit: Annotated[
        int | None, Field(ge=1, description="Max replies (omitted: the configured cap).")
    ] = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Comment]:
    """A comment and its replies, reconstructed from the page's comment list.

    The Wiki ``/thread`` endpoint (``comments_thread_get``) is dead (returns no replies), so this
    fetches every comment on the page and chains ``parent_id`` from the target: the comment comes
    first, then its descendants in depth-first order. Capped at the configured item cap unless
    ``limit`` is given. Use ``comments_list`` first to discover a root comment id, then this to
    read its thread.
    """
    cap = config.http.cap(limit)
    return client.comments.thread_list(page_id=page_id, comment_id=comment_id, limit=cap)


@mcp.tool(
    name="comments_thread_get",
    annotations={**RO, "title": "Get Wiki comment thread from the server"},
)
def thread_get(
    page_id: Annotated[int, Field(description="Numeric page id the comment lives on.")],
    comment_id: Annotated[int, Field(description="Comment id whose server-side thread to fetch.")],
    limit: Annotated[
        int | None, Field(ge=1, description="Max comments (omitted: the configured cap).")
    ] = None,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Comment]:
    """The thread of a comment as the Wiki server returns it — an empty list for every real thread.

    Checked live on 2026-10-02: the server's ``/thread`` endpoint has no replies to give, for a
    root comment or a reply, plain or inline. Use ``comments_thread_list``, which rebuilds the
    thread from the page's comment list.
    """
    cap = config.http.cap(limit)
    return client.comments.thread_get(page_id=page_id, comment_id=comment_id, limit=cap)


@mcp.tool(name="comments_create", annotations={**WRITE, "title": "Create Wiki comment"})
def create(
    page_id: Annotated[int, Field(description="Numeric id of the page to comment on.")],
    body: Annotated[
        CommentCreate,
        Field(
            description="The comment: required ``body`` text plus optional placement — "
            "``inline_text`` (pin to a page fragment), ``parent_id`` (reply), ``thread_id``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> CommentCreated:
    """Add a comment (or a threaded reply) to a wiki page.

    Pass ``body.parent_id`` to reply to an existing comment — find ids with
    ``comments_list``. Returns the created comment with its numeric ``id``.
    """
    return client.comments.create(page_id=page_id, body=body)


@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Wiki comment"},
)
def delete(
    page_id: Annotated[int, Field(description="Numeric id of the page the comment lives on.")],
    comment_id: Annotated[int, Field(description="Numeric id of the comment to delete.")],
    client: WikiClient = Depends(wiki_client),
) -> CommentDeleteResult:
    """Delete a comment from a wiki page — irreversible (no recovery token).

    Returns the page's remaining ``comments_count``. Verify the target with
    ``comments_list`` / ``comments_thread_list`` first: deleting a parent orphans its
    replies' threading.
    """
    return client.comments.delete(page_id=page_id, comment_id=comment_id)
