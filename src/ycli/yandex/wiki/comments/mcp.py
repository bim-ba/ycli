"""Wiki /pages/{id}/comments FastMCP tools."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.comments.models import (
    CommentCreate,
    CommentCreated,
    CommentDeleteResult,
    CommentList,
)
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    app_config,
    wiki_client,
)

mcp = FastMCP("wiki-comments")


@mcp.tool(name="comments_list", annotations={**RO, "title": "List Wiki comments"}, tags=TAGS)
def list_(
    page_id: int,
    limit: int = 0,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> CommentList:
    """Comments on a page id, auto-paginated (drains the ``next_cursor`` internally).

    Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is given. Pair with
    ``pages_meta`` (its ``attributes.comments_count`` tells you how many exist).
    """
    cap = resolve_cap(limit, config.max_items)
    return client.comments.list(page_id=page_id, limit=cap)


@mcp.tool(
    name="comments_thread_list", annotations={**RO, "title": "List Wiki comment thread"}, tags=TAGS
)
def thread_list(
    page_id: Annotated[int, Field(description="Numeric page id the comment lives on.")],
    comment_id: Annotated[int, Field(description="Root comment id whose reply thread to fetch.")],
    limit: Annotated[int, Field(description="Max replies (0 = YCLI_MAX_ITEMS cap).")] = 0,
    client: WikiClient = Depends(wiki_client),
    config: AppConfig = Depends(app_config),
) -> CommentList:
    """A comment and its replies, reconstructed from the page's comment list.

    The Wiki ``/thread`` endpoint is dead (returns no replies), so this fetches every comment
    on the page and chains ``parent_id`` from the target: the comment comes first, then its
    descendants in depth-first order. Capped at YCLI_MAX_ITEMS (default 500) unless ``limit`` is
    given. Use ``comments_list`` first to discover a root comment id, then this to read its thread.

    Example:
        >>> thread_list(page_id=12345, comment_id=678, limit=50)  # doctest: +SKIP
    """
    cap = resolve_cap(limit, config.max_items)
    return client.comments.thread(page_id=page_id, comment_id=comment_id, limit=cap)


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

    Example:
        >>> create(page_id=12345, body={"body": "LGTM", "parent_id": 7})  # doctest: +SKIP
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

    Example:
        >>> delete(page_id=12345, comment_id=678)  # doctest: +SKIP
    """
    return client.comments.delete(page_id=page_id, comment_id=comment_id)
