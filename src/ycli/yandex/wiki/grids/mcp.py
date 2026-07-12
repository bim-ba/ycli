"""Wiki /grids FastMCP tools — full read/write mirror of the grids SDK surface.

Every write except ``grids_create`` and ``grids_clone`` carries the grid's current
``revision`` (optimistic lock) — read it off ``grids_get`` or the previous write's reply.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    wiki_client,
)
from ycli.yandex.wiki.grids.models import (
    CellsUpdate,
    CellsUpdateResult,
    ColumnsAdd,
    ColumnsMove,
    ColumnsRemove,
    Grid,
    GridActionResult,
    GridClone,
    GridCloneOperation,
    GridCreate,
    GridUpdate,
    RevisionResult,
    RowsAdd,
    RowsAddResult,
    RowsMove,
    RowsRemove,
)

mcp = FastMCP("wiki-grids")

GridIdParam = Annotated[str, Field(description="The grid's permanent UUID4 id.")]


@mcp.tool(name="grids_get", annotations={**RO, "title": "Get Wiki grid"}, tags=TAGS)
def get(
    grid_id: Annotated[str, Field(description="The grid's permanent UUID4 id.")],
    fields: Annotated[
        str | None,
        Field(description="Extra blocks to include (CSV), e.g. ``attributes,user_permissions``."),
    ] = None,
    row_filter: Annotated[
        str | None, Field(description="Server-side row filter, e.g. ``[slug] ~ wiki``.")
    ] = None,
    only_cols: Annotated[
        str | None, Field(description="Return only these column slugs (CSV).")
    ] = None,
    only_rows: Annotated[str | None, Field(description="Return only these row ids (CSV).")] = None,
    sort: Annotated[str | None, Field(description="Row sort, e.g. ``slug,-slug2``.")] = None,
    client: WikiClient = Depends(wiki_client),
) -> Grid:
    """A single dynamic table (grid) by its UUID, with structure, rows and revision.

    Grids are the modern dynamic tables attached to a page; find a grid's id with
    ``pages_grids_list``. Use ``filter``/``only_cols``/``only_rows``/``sort`` to narrow large
    grids server-side, and ``fields=attributes,user_permissions`` for extra blocks. The returned
    ``revision`` is the optimistic-lock token any subsequent write (via the CLI/SDK) must echo.

    Example:
        >>> grids_get(grid_id="g-uuid", only_cols="name,owner")  # doctest: +SKIP
    """
    return client.grids.get(
        grid_id,
        fields=fields,
        row_filter=row_filter,
        only_cols=only_cols,
        only_rows=only_rows,
        sort=sort,
    )


@mcp.tool(name="grids_create", annotations={**WRITE, "title": "Create Wiki grid"}, tags=WRITE_TAGS)
def create(
    body: Annotated[
        GridCreate,
        Field(description="Grid spec: ``title`` plus the ``page`` (by id or slug) to live on."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> Grid:
    """Create an empty dynamic table (grid) as a resource of a page.

    A new grid has no rows or columns — add them afterwards with ``grids_add_columns`` and
    ``grids_add_rows``. Returns the created grid; its ``revision`` seeds the optimistic lock
    every subsequent write must echo.

    Example:
        >>> create(body={"title": "Roadmap", "page": {"slug": "data/x"}})  # doctest: +SKIP
    """
    return client.grids.create(body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki grid"},
    tags=WRITE_TAGS,
)
def update(
    grid_id: GridIdParam,
    body: Annotated[
        GridUpdate,
        Field(
            description="Editable fields (``title``, ``default_sort``) plus the required "
            "``revision`` (optimistic lock)."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Rename or re-sort a grid (POST-not-PATCH quirk handled by the SDK).

    ``body.revision`` must match the grid's current revision (read it off ``grids_get``);
    a mismatch fails the write. Returns the grid's new ``revision``.

    Example:
        >>> update(grid_id="g-uuid", body={"revision": "3", "title": "New"})  # doctest: +SKIP
    """
    return client.grids.update(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_delete", annotations={**DESTRUCTIVE, "title": "Delete Wiki grid"}, tags=WRITE_TAGS
)
def delete(
    grid_id: GridIdParam,
    client: WikiClient = Depends(wiki_client),
) -> GridActionResult:
    """Delete a grid — irreversible (grids have NO recovery token, unlike pages).

    Verify the target with ``grids_get`` first. The API answers ``204 No Content``; the
    result is a typed acknowledgement.

    Example:
        >>> delete(grid_id="g-uuid")  # doctest: +SKIP
    """
    return client.grids.delete(grid_id)


@mcp.tool(
    name="grids_add_rows", annotations={**WRITE, "title": "Add Wiki grid rows"}, tags=WRITE_TAGS
)
def add_rows(
    grid_id: GridIdParam,
    body: Annotated[
        RowsAdd,
        Field(
            description="``rows`` (each maps column slug → cell value) + ``revision``; "
            "optional ``position`` / ``after_row_id`` placement."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RowsAddResult:
    """Insert rows into a grid at a position (default: append at the end).

    Column slugs come from ``grids_get``'s structure block. Returns the created rows plus
    the grid's new ``revision``.

    Example:
        >>> add_rows(
        ...     grid_id="g-uuid", body={"revision": "3", "rows": [{"name": "x"}]}
        ... )  # doctest: +SKIP
    """
    return client.grids.add_rows(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_remove_rows",
    annotations={**DESTRUCTIVE, "title": "Remove Wiki grid rows"},
    tags=WRITE_TAGS,
)
def remove_rows(
    grid_id: GridIdParam,
    body: Annotated[
        RowsRemove,
        Field(description="``row_ids`` to delete (at least one) + the current ``revision``."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Delete rows from a grid by id — irreversible.

    A rare DELETE-with-body: ids and revision travel in the JSON body. Find row ids with
    ``grids_get``. Returns the grid's new ``revision``.

    Example:
        >>> remove_rows(
        ...     grid_id="g-uuid", body={"revision": "3", "row_ids": ["r1"]}
        ... )  # doctest: +SKIP
    """
    return client.grids.remove_rows(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_move_rows", annotations={**WRITE, "title": "Move Wiki grid rows"}, tags=WRITE_TAGS
)
def move_rows(
    grid_id: GridIdParam,
    body: Annotated[
        RowsMove,
        Field(
            description="``row_id`` (first row to move) + destination (``position`` or "
            "``after_row_id``) + optional ``rows_count`` + the current ``revision``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Reorder rows inside a grid (move a run of consecutive rows to a new position).

    Returns the grid's new ``revision``.

    Example:
        >>> move_rows(
        ...     grid_id="g-uuid", body={"revision": "3", "row_id": "r1", "position": 0}
        ... )  # doctest: +SKIP
    """
    return client.grids.move_rows(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_add_columns",
    annotations={**WRITE, "title": "Add Wiki grid columns"},
    tags=WRITE_TAGS,
)
def add_columns(
    grid_id: GridIdParam,
    body: Annotated[
        ColumnsAdd,
        Field(
            description="``columns`` (each needs ``title`` + ``type``) + the current "
            "``revision``; optional ``position``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Add columns to a grid at a position (default: append after the last column).

    Each column needs a ``title`` and a ``type`` (``string``, ``number``, ``select``,
    ``staff``, ``date``, ``checkbox``, ``ticket_field``, …); type-specific fields such as
    ``select_options`` shape it further. Returns the grid's new ``revision``.

    Example:
        >>> add_columns(
        ...     grid_id="g-uuid",
        ...     body={"revision": "3", "columns": [{"title": "C", "type": "string"}]},
        ... )  # doctest: +SKIP
    """
    return client.grids.add_columns(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_remove_columns",
    annotations={**DESTRUCTIVE, "title": "Remove Wiki grid columns"},
    tags=WRITE_TAGS,
)
def remove_columns(
    grid_id: GridIdParam,
    body: Annotated[
        ColumnsRemove,
        Field(description="``column_slugs`` to delete + the current ``revision``."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Delete columns from a grid by slug — irreversible (every cell in them is lost).

    A rare DELETE-with-body: slugs and revision travel in the JSON body. Returns the grid's
    new ``revision``.

    Example:
        >>> remove_columns(
        ...     grid_id="g-uuid", body={"revision": "3", "column_slugs": ["name"]}
        ... )  # doctest: +SKIP
    """
    return client.grids.remove_columns(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_move_columns",
    annotations={**WRITE, "title": "Move Wiki grid columns"},
    tags=WRITE_TAGS,
)
def move_columns(
    grid_id: GridIdParam,
    body: Annotated[
        ColumnsMove,
        Field(
            description="``column_slug`` (first column to move) + ``position`` + optional "
            "``columns_count`` + the current ``revision``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Reorder columns inside a grid (move a run of consecutive columns to a new position).

    Returns the grid's new ``revision``.

    Example:
        >>> move_columns(
        ...     grid_id="g-uuid", body={"revision": "3", "column_slug": "name", "position": 0}
        ... )  # doctest: +SKIP
    """
    return client.grids.move_columns(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(
    name="grids_update_cells",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki grid cells"},
    tags=WRITE_TAGS,
)
def update_cells(
    grid_id: GridIdParam,
    body: Annotated[
        CellsUpdate,
        Field(
            description="``cells`` (each: ``row_id`` + ``column_slug`` + ``value``) + the "
            "current ``revision``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> CellsUpdateResult:
    """Set the value of individual grid cells (addressed by row id + column slug).

    Repeating the same call sets the same values (idempotent). Returns the updated cells
    plus the grid's new ``revision``.

    Example:
        >>> update_cells(
        ...     grid_id="g-uuid",
        ...     body={
        ...         "revision": "3",
        ...         "cells": [{"row_id": 1, "column_slug": "name", "value": "x"}],
        ...     },
        ... )  # doctest: +SKIP
    """
    return client.grids.update_cells(grid_id, body=body.model_dump(exclude_none=True))


@mcp.tool(name="grids_clone", annotations={**WRITE, "title": "Clone Wiki grid"}, tags=WRITE_TAGS)
def clone(
    grid_id: GridIdParam,
    body: Annotated[
        GridClone,
        Field(
            description="Clone spec: ``target`` page slug (created if absent) + optional "
            "``title`` and ``with_data`` (copy rows too)."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> GridCloneOperation:
    """Copy a grid onto another page (``POST /grids/{id}/clone`` — asynchronous).

    ``body.with_data=true`` copies the rows as well as the structure. Returns a deferred
    operation reference — poll ``operations_gridclone_get`` with the returned
    ``operation.id`` until it reaches a terminal status.

    Example:
        >>> clone(grid_id="g-uuid", body={"target": "data/y"})  # doctest: +SKIP
    """
    return client.grids.clone(grid_id, body=body.model_dump(exclude_none=True))
