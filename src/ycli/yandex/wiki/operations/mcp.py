"""Wiki /operations FastMCP tools — reads only; poll a clone to completion from an agent."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, TAGS, wiki_client
from ycli.yandex.wiki.operations.models import CloneOperationStatus, GridCloneOperationStatus

mcp = FastMCP("wiki-operations")


@mcp.tool(
    name="operations_clone_get",
    annotations={**RO, "title": "Get Wiki page-clone status"},
    tags=TAGS,
)
def clone_get(
    task_id: Annotated[str, Field(description="Task id from a page-clone trigger (operation.id).")],
    client: WikiClient = Depends(wiki_client),
) -> CloneOperationStatus:
    """Status of an async page-clone operation — poll it until it finishes.

    ``pages clone`` (a CLI/SDK write) returns an ``operation.id``; pass it here and re-read until
    ``status`` is ``success`` or ``failed``. On ``success`` the ``result.page`` names the clone.
    The sibling ``operations_gridclone_get`` polls inline-grid clones instead.

    Example:
        >>> operations_clone_get(task_id="task-1")  # doctest: +SKIP
    """
    return client.operations.clone_get(task_id)


@mcp.tool(
    name="operations_gridclone_get",
    annotations={**RO, "title": "Get Wiki grid-clone status"},
    tags=TAGS,
)
def gridclone_get(
    task_id: Annotated[str, Field(description="Task id from a grid-clone trigger (operation.id).")],
    client: WikiClient = Depends(wiki_client),
) -> GridCloneOperationStatus:
    """Status of an async inline-grid-clone operation — poll it until it finishes.

    ``grids clone`` (a CLI/SDK write) returns an ``operation.id``; pass it here and re-read until
    ``status`` is ``success`` or ``failed``. On ``success`` the ``result.grid_id`` names the copy.
    The sibling ``operations_clone_get`` polls page clones instead.

    Example:
        >>> operations_gridclone_get(task_id="task-1")  # doctest: +SKIP
    """
    return client.operations.gridclone_get(task_id)
