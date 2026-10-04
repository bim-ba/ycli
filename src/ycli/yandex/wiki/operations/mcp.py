"""Wiki /operations FastMCP tools — reads only; poll a clone or move to completion."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import RO, wiki_client
from ycli.yandex.wiki.operations.models import (
    CloneOperationStatus,
    GridCloneOperationStatus,
    MoveOperationStatus,
)

mcp = FastMCP("wiki-operations")


@mcp.tool(
    name="operations_clone_get",
    annotations={**RO, "title": "Get Wiki page-clone status"},
)
def clone_get(
    task_id: Annotated[str, Field(description="Task id from a page-clone trigger (operation.id).")],
    client: WikiClient = Depends(wiki_client),
) -> CloneOperationStatus:
    """Status of an async page-clone operation — poll it until it finishes.

    ``pages clone`` (a CLI/SDK write) returns an ``operation.id``; pass it here and re-read until
    ``status`` is ``success`` or ``failed``. On ``success`` the ``result.page`` names the clone.
    The sibling ``operations_gridclone_get`` polls inline-grid clones instead.
    """
    return client.operations.clone_get(task_id)


@mcp.tool(
    name="operations_gridclone_get",
    annotations={**RO, "title": "Get Wiki grid-clone status"},
)
def gridclone_get(
    task_id: Annotated[str, Field(description="Task id from a grid-clone trigger (operation.id).")],
    client: WikiClient = Depends(wiki_client),
) -> GridCloneOperationStatus:
    """Status of an async inline-grid-clone operation — poll it until it finishes.

    ``grids clone`` (a CLI/SDK write) returns an ``operation.id``; pass it here and re-read until
    ``status`` is ``success`` or ``failed``. On ``success`` the ``result.grid_id`` names the copy.
    The sibling ``operations_clone_get`` polls page clones instead.
    """
    return client.operations.gridclone_get(task_id)


@mcp.tool(
    name="operations_move_get",
    annotations={**RO, "title": "Get Wiki page-move status"},
)
def move_get(
    task_id: Annotated[str, Field(description="Task id from a page-move trigger (operation.id).")],
    client: WikiClient = Depends(wiki_client),
) -> MoveOperationStatus:
    """Status of an async page-move operation — poll it until it finishes.

    ``pages_move`` returns an ``operation.id``; pass it here and re-read until ``status`` is
    ``success`` or ``failed``. On ``success`` the ``result.page_count`` says how many pages moved.
    This operation is undocumented by Yandex (it is in the live OpenAPI only) and may change.
    """
    return client.operations.move_get(task_id)
