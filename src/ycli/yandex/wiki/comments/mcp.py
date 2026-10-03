"""Wiki /pages/{id}/comments FastMCP tools."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
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
    TAGS,
    WRITE,
    WRITE_TAGS,
    PageId,
    app_config,
    wiki_client,
)

mcp = FastMCP("wiki-comments")


@mcp.tool(name="comments_list", annotations={**RO, "title": "List Wiki comments"}, tags=TAGS)
def list_(
    page_id: PageId,
    limit: Annotated[int, Field(description=f"Max comments to return; {LIMIT_CAP}")] = 0,
    order_by: Annotated[str, Field(description="Sort field: ``created_at``.")] = "",
    order_direction: Annotated[
        str, Field(description="Sort direction for ``order_by``: ``asc`` or ``desc``.")
    ] = "",
    status_filter: Annotated[
        str, Field(description="Keep only ``resolved`` or only ``unresolved`` comments.")
    ] = "",
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[Comment]:
    """Comments on a page id, auto-paginated (drains the ``next_cursor`` internally).

    Capped at the configured item cap unless ``limit`` is given. Pair with
    ``pages_meta`` (its ``attributes.comments_count`` tells you how many exist).
    """
    cap = config.http.cap(limit)
    return client.comments.list(
        page_id=page_id,
        limit=cap,
        order_by=order_by or None,
        order_direction=order_direction or None,
        status_filter=status_filter or None,
    )


@mcp.tool(
    name="comments_thread_list", annotations={**RO, "title": "List Wiki comment thread"}, tags=TAGS
)
def thread_list(
    page_id: Annotated[int, Field(description="Numeric page id the comment lives on.")],
    comment_id: Annotated[int, Field(description="Root comment id whose reply thread to fetch.")],
    limit: Annotated[int, Field(description="Max replies (0 = configured cap).")] = 0,
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
    return client.comments.thread(page_id=page_id, comment_id=comment_id, limit=cap)


@mcp.tool(
    name="comments_thread_get",
    annotations={**RO, "title": "Get Wiki comment thread from the server"},
    tags=TAGS,
)
def thread_get(
    page_id: Annotated[int, Field(description="Numeric page id the comment lives on.")],
    comment_id: Annotated[int, Field(description="Comment id whose server-side thread to fetch.")],
    limit: Annotated[int, Field(description="Max comments (0 = configured cap).")] = 0,
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


@mcp.tool(
    name="comments_create", annotations={**WRITE, "title": "Create Wiki comment"}, tags=WRITE_TAGS
)
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
    return client.comments.create(page_id=page_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Wiki comment"},
    tags=WRITE_TAGS,
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
