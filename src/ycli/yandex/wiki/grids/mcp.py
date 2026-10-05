"""Wiki /grids FastMCP tools — full read/write mirror of the grids SDK surface.

Every write except ``grids_create`` and ``grids_clone`` carries the grid's current
``revision`` — read it off ``grids_get`` or the previous write's reply. The API refuses
(409) only a cell changed after that revision; every other write passes with a stale one.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.models import Ack
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    wiki_client,
)
from ycli.yandex.wiki.grids.models import (
    CellsUpdate,
    CellsUpdateResult,
    ColumnsAdd,
    ColumnsMove,
    ColumnsRemove,
    ColumnSuggest,
    ColumnSuggestion,
    ColumnUpdate,
    ColumnUpdateResult,
    Grid,
    GridClone,
    GridCreate,
    GridUpdate,
    RevisionResult,
    RowsAdd,
    RowsAddResult,
    RowsMove,
    RowsRemove,
    RowUpdate,
    RowUpdateResult,
)
from ycli.yandex.wiki.models import AsyncOperation

mcp = FastMCP("wiki-grids")

GridIDParam = Annotated[str, Field(description="The grid's permanent UUID4 id.")]


@mcp.tool(name="grids_get", annotations={**RO, "title": "Get Wiki grid"})
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
    revision: Annotated[
        str | None, Field(description="Load this past revision instead of the current one.")
    ] = None,
    sort: Annotated[str | None, Field(description="Row sort, e.g. ``slug,-slug2``.")] = None,
    client: WikiClient = Depends(wiki_client),
) -> Grid:
    """A single dynamic table (grid) by its UUID, with structure, rows and revision.

    Grids are the modern dynamic tables attached to a page; find a grid's id with
    ``pages_grids_list``. Use ``row_filter``/``only_cols``/``only_rows``/``sort`` to narrow large
    grids server-side, and ``fields=attributes,user_permissions`` for extra blocks. The returned
    ``revision`` is what any subsequent write must send back.
    """
    return client.grids.get(
        grid_id,
        fields=fields,
        row_filter=row_filter,
        only_cols=only_cols,
        only_rows=only_rows,
        revision=revision,
        sort=sort,
    )


@mcp.tool(name="grids_create", annotations={**WRITE, "title": "Create Wiki grid"})
def create(
    body: Annotated[
        GridCreate,
        Field(description="Grid spec: ``title`` plus the ``page`` (by id or slug) to live on."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> Grid:
    """Create an empty dynamic table (grid) as a resource of a page.

    A new grid has no rows or columns — add them afterwards with ``grids_columns_create`` and
    ``grids_rows_create``. Returns the created grid; every subsequent write sends its
    ``revision`` back.
    """
    return client.grids.create(body=body)


@mcp.tool(
    name="grids_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki grid"},
)
def update(
    grid_id: GridIDParam,
    body: Annotated[
        GridUpdate,
        Field(
            description="Editable fields (``title``, ``default_sort``) plus the required "
            "``revision``."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Rename or re-sort a grid (POST-not-PATCH quirk handled by the SDK).

    ``body.revision`` must match the grid's current revision (read it off ``grids_get``);
    a mismatch fails the write. Returns the grid's new ``revision``.
    """
    return client.grids.update(grid_id, body=body)


@mcp.tool(name="grids_delete", annotations={**DESTRUCTIVE, "title": "Delete Wiki grid"})
def delete(
    grid_id: GridIDParam,
    client: WikiClient = Depends(wiki_client),
) -> Ack:
    """Delete a grid — irreversible (grids have NO recovery token, unlike pages).

    Verify the target with ``grids_get`` first. The API answers ``204 No Content``; the
    result is a typed acknowledgement.
    """
    return client.grids.delete(grid_id)


@mcp.tool(name="grids_rows_create", annotations={**WRITE, "title": "Add Wiki grid rows"})
def rows_create(
    grid_id: GridIDParam,
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
    """
    return client.grids.rows_create(grid_id, body=body)


@mcp.tool(
    name="grids_rows_delete",
    annotations={**DESTRUCTIVE, "title": "Remove Wiki grid rows"},
)
def rows_delete(
    grid_id: GridIDParam,
    body: Annotated[
        RowsRemove,
        Field(description="``row_ids`` to delete (at least one) + the current ``revision``."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Delete rows from a grid by id — irreversible.

    A rare DELETE-with-body: ids and revision travel in the JSON body. Find row ids with
    ``grids_get``. Returns the grid's new ``revision``.
    """
    return client.grids.rows_delete(grid_id, body=body)


@mcp.tool(name="grids_rows_move", annotations={**WRITE, "title": "Move Wiki grid rows"})
def rows_move(
    grid_id: GridIDParam,
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
    """
    return client.grids.rows_move(grid_id, body=body)


@mcp.tool(
    name="grids_columns_create",
    annotations={**WRITE, "title": "Add Wiki grid columns"},
)
def columns_create(
    grid_id: GridIDParam,
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
    """
    return client.grids.columns_create(grid_id, body=body)


@mcp.tool(
    name="grids_columns_delete",
    annotations={**DESTRUCTIVE, "title": "Remove Wiki grid columns"},
)
def columns_delete(
    grid_id: GridIDParam,
    body: Annotated[
        ColumnsRemove,
        Field(description="``column_slugs`` to delete + the current ``revision``."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RevisionResult:
    """Delete columns from a grid by slug — irreversible (every cell in them is lost).

    A rare DELETE-with-body: slugs and revision travel in the JSON body. Returns the grid's
    new ``revision``.
    """
    return client.grids.columns_delete(grid_id, body=body)


@mcp.tool(
    name="grids_columns_move",
    annotations={**WRITE, "title": "Move Wiki grid columns"},
)
def columns_move(
    grid_id: GridIDParam,
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
    """
    return client.grids.columns_move(grid_id, body=body)


@mcp.tool(
    name="grids_cells_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki grid cells"},
)
def cells_update(
    grid_id: GridIDParam,
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
    """
    return client.grids.cells_update(grid_id, body=body)


@mcp.tool(name="grids_clone", annotations={**WRITE, "title": "Clone Wiki grid"})
def clone(
    grid_id: GridIDParam,
    body: Annotated[
        GridClone,
        Field(
            description="Clone spec: ``target`` page slug (created if absent) + optional "
            "``title`` and ``with_data`` (copy rows too)."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> AsyncOperation:
    """Copy a grid onto another page (``POST /grids/{id}/clone`` — asynchronous).

    ``body.with_data=true`` copies the rows as well as the structure. Returns a deferred
    operation reference — poll ``operations_clone_inline_grid_get`` with the returned
    ``operation.id`` until it reaches a terminal status.
    """
    return client.grids.clone(grid_id, body=body)


@mcp.tool(
    name="grids_columns_suggest",
    annotations={**RO, "title": "Suggest Wiki grid column slug"},
)
def columns_suggest(
    grid_id: GridIDParam,
    body: Annotated[
        ColumnSuggest,
        Field(description="``slug`` to check, or a ``title`` to turn into a slug and check."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> ColumnSuggestion:
    """Check whether a column slug is free in a grid and get free alternatives (read-only).

    The call is a POST but changes nothing. Yandex does not document this operation (it is in
    the live OpenAPI only) and may change it.
    """
    return client.grids.columns_suggest(grid_id, body=body)


@mcp.tool(
    name="grids_columns_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki grid column"},
)
def columns_update(
    grid_id: GridIDParam,
    column_slug: Annotated[str, Field(description="Slug of the column to edit.")],
    body: Annotated[
        ColumnUpdate,
        Field(
            description="The fields to change (``title``, ``description``, ``required``, "
            "``width``, ``color``, ``pinned``, ``select_options``, …); ``revision`` is optional."
        ),
    ],
    client: WikiClient = Depends(wiki_client),
) -> ColumnUpdateResult:
    """Edit a grid column in place: only the fields sent change; its type and slug stay.

    Repeating the same call leaves the same column (idempotent). ``revision`` is accepted but not
    enforced, and every call moves the grid's revision on. Returns the grid's new ``revision`` and
    the column as saved. Yandex does not document this operation (it is in the
    live OpenAPI only) and may change it.
    """
    return client.grids.columns_update(grid_id, column_slug, body=body)


@mcp.tool(
    name="grids_rows_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update Wiki grid row"},
)
def rows_update(
    grid_id: GridIDParam,
    row_id: Annotated[str, Field(description="Id of the row to pin or colour.")],
    body: Annotated[
        RowUpdate,
        Field(description="``pinned`` and/or ``color`` to set; ``revision`` is optional."),
    ],
    client: WikiClient = Depends(wiki_client),
) -> RowUpdateResult:
    """Pin or colour one grid row (cell values are set by ``grids_cells_update``).

    Repeating the same call leaves the same row (idempotent). The reply is a bare acknowledgement
    without the new revision (read it with ``grids_get``); ``revision`` is accepted but not
    enforced. Yandex does not document this operation (it is in the live OpenAPI only) and may
    change it.
    """
    return client.grids.rows_update(grid_id, row_id, body=body)
