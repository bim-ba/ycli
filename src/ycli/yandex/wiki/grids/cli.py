"""`wiki grids` commands — dynamic-table CRUD plus rows/columns/cells and async clone.

Structured bodies (rows, columns, cells, default-sort) are passed as JSON strings and parsed
into the typed request models before sending. Every mutating call takes ``--revision`` (the
revision read off ``grids get``, which the edit is based on) except ``create``. ``clone`` is
asynchronous: ``--wait`` (default) polls the ``operations`` resource to a terminal state.
"""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.progress import wait_for
from ycli.cli.typedefs import values_option
from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.grids.models import (
    BGColor,
    CellsUpdate,
    CellsUpdateResult,
    ColumnPinType,
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
    WidthUnits,
)
from ycli.yandex.wiki.models import AsyncOperation, PageIdentity
from ycli.yandex.wiki.operations.models import GridCloneOperationStatus

app = typer.Typer(name="grids", help="Wiki dynamic tables (grids).", no_args_is_help=True)
rows_app = typer.Typer(name="rows", help="Grid rows.", no_args_is_help=True)
columns_app = typer.Typer(name="columns", help="Grid columns.", no_args_is_help=True)
cells_app = typer.Typer(name="cells", help="Grid cells.", no_args_is_help=True)


app.add_typer(rows_app)
app.add_typer(columns_app)
app.add_typer(cells_app)

GridIDArg = Annotated[str, typer.Argument(metavar="GRID_ID", help="Grid UUID.")]
RevisionOpt = Annotated[
    str | None, typer.Option("--revision", help="Grid revision the edit is based on.")
]
OptionalRevisionOpt = Annotated[
    str | None,
    typer.Option("--revision", help="Grid revision (this endpoint does not enforce it)."),
]
PositionOpt = Annotated[int | None, typer.Option("--position", help="Zero-based target index.")]


@app.command()
def get(
    grid_id: GridIDArg,
    fields: Annotated[
        str | None, typer.Option(help="Extra blocks, e.g. attributes,user_permissions.")
    ] = None,
    row_filter: Annotated[
        str | None, typer.Option("--row-filter", help="Row filter expr, e.g. [slug] ~ wiki.")
    ] = None,
    only_cols: Annotated[
        str | None, typer.Option("--only-cols", help="Only these column slugs (CSV).")
    ] = None,
    only_rows: Annotated[
        str | None, typer.Option("--only-rows", help="Only these row ids (CSV).")
    ] = None,
    revision: Annotated[
        str | None, typer.Option("--revision", help="Load a historical revision.")
    ] = None,
    sort: Annotated[str | None, typer.Option(help="Row sort, e.g. slug,-slug2.")] = None,
    *,
    wiki: WikiClient,
) -> Grid:
    """Fetch a grid by GRID_ID (GET /grids/{id}); read its revision to drive later writes."""
    return wiki.grids.get(
        grid_id,
        fields=fields,
        row_filter=row_filter,
        only_cols=only_cols,
        only_rows=only_rows,
        revision=revision,
        sort=sort,
    )


@app.command()
def create(
    title: Annotated[str, typer.Option(help="Title of the new grid.")],
    page_slug: Annotated[
        str | None, typer.Option("--page-slug", help="Target page slug, e.g. data/x.")
    ] = None,
    page_id: Annotated[
        int | None, typer.Option("--page-id", help="Target page numeric id.")
    ] = None,
    *,
    wiki: WikiClient,
) -> Grid:
    """Create a grid on a page (POST /grids); name the page by --page-slug or --page-id."""
    body = GridCreate(title=title, page=PageIdentity(id=page_id, slug=page_slug))
    return wiki.grids.create(body=body)


@app.command()
def update(
    grid_id: GridIDArg,
    revision: RevisionOpt = None,
    title: Annotated[str | None, typer.Option(help="New grid title.")] = None,
    default_sort: Annotated[
        str | None,
        typer.Option(
            "--default-sort",
            help="New default sort as JSON in the write shape "
            '\'[{"<column_slug>": "asc"|"desc"}]\', e.g. \'[{"priority": "desc"}]\'.',
        ),
    ] = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Rename / re-sort a grid (POST /grids/{id}; POST not PATCH).

    ``--default-sort`` takes the API's write shape (column slug → direction mappings), not the
    ``{slug, title, direction}`` read shape that ``grids get`` returns.
    """
    body = GridUpdate(
        revision=revision,
        title=title,
        default_sort=json.loads(default_sort) if default_sort is not None else None,
    )
    return wiki.grids.update(grid_id, body=body)


@app.command()
def delete(grid_id: GridIDArg, *, wiki: WikiClient) -> Ack:
    """Delete a grid (DELETE /grids/{id})."""
    return wiki.grids.delete(grid_id)


@app.command()
def clone(
    grid_id: GridIDArg,
    target: Annotated[
        str, typer.Option("--target", help="Destination page slug (created if absent).")
    ],
    title: Annotated[str | None, typer.Option(help="Title of the copy, if renaming.")] = None,
    with_data: Annotated[
        bool | None,
        typer.Option(
            "--with-data/--no-with-data", help="Copy the rows too, not just the structure."
        ),
    ] = None,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> AsyncOperation | GridCloneOperationStatus:
    """Copy a grid onto another page (POST /grids/{id}/clone; async). --wait polls to completion."""
    body = GridClone(target=target, title=title, with_data=with_data)
    operation = wiki.grids.clone(grid_id, body=body)
    if wait and operation.operation is not None and operation.operation.id is not None:
        task_id = operation.operation.id
        status = wait_for(
            lambda: wiki.operations.clone_inline_grid_get(task_id),
            lambda state: state.is_terminal,
            message="Waiting for grid clone…",
            max_wait_seconds=config.http.max_wait_seconds,
        )
        return status
    return operation


@rows_app.command("create")
def rows_create(
    grid_id: GridIDArg,
    rows: Annotated[
        str, typer.Option("--rows", help='Rows as JSON, e.g. \'[{"name":"x"}]\' (slug→value).')
    ],
    revision: RevisionOpt = None,
    position: PositionOpt = None,
    after_row_id: Annotated[
        str | None, typer.Option("--after-row-id", help="Insert after this row id.")
    ] = None,
    *,
    wiki: WikiClient,
) -> RowsAddResult:
    """Insert rows into a grid (POST /grids/{id}/rows)."""
    body = RowsAdd(
        revision=revision,
        rows=json.loads(rows),
        position=position,
        after_row_id=after_row_id,
    )
    return wiki.grids.rows_create(grid_id, body=body)


@rows_app.command("delete")
def rows_delete(
    grid_id: GridIDArg,
    row_id: Annotated[list[str], typer.Option("--row-id", help="Row id to delete (repeatable).")],
    revision: RevisionOpt = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Delete rows from a grid by id (DELETE /grids/{id}/rows)."""
    body = RowsRemove(revision=revision, row_ids=row_id)
    return wiki.grids.rows_delete(grid_id, body=body)


@rows_app.command("move")
def rows_move(
    grid_id: GridIDArg,
    row_id: Annotated[str, typer.Option("--row-id", help="Id of the first row to move.")],
    revision: RevisionOpt = None,
    after_row_id: Annotated[
        str | None, typer.Option("--after-row-id", help="Move to just after this row id.")
    ] = None,
    position: PositionOpt = None,
    rows_count: Annotated[
        int | None, typer.Option("--rows-count", help="How many consecutive rows to move.")
    ] = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Reorder rows in a grid (POST /grids/{id}/rows/move)."""
    body = RowsMove(
        revision=revision,
        row_id=row_id,
        after_row_id=after_row_id,
        position=position,
        rows_count=rows_count,
    )
    return wiki.grids.rows_move(grid_id, body=body)


@columns_app.command("create")
def columns_create(
    grid_id: GridIDArg,
    columns: Annotated[
        str,
        typer.Option(
            "--columns",
            help='Columns as JSON, e.g. \'[{"title":"C","type":"string","slug":"c"}]\'.',
        ),
    ],
    revision: RevisionOpt = None,
    position: PositionOpt = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Add columns to a grid (POST /grids/{id}/columns).

    The API requires a ``slug`` on every column.
    """
    body = ColumnsAdd(revision=revision, columns=json.loads(columns), position=position)
    return wiki.grids.columns_create(grid_id, body=body)


@columns_app.command("delete")
def columns_delete(
    grid_id: GridIDArg,
    column_slug: Annotated[
        list[str], typer.Option("--column-slug", help="Column slug to delete (repeatable).")
    ],
    revision: RevisionOpt = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Delete columns from a grid by slug (DELETE /grids/{id}/columns)."""
    body = ColumnsRemove(revision=revision, column_slugs=column_slug)
    return wiki.grids.columns_delete(grid_id, body=body)


@columns_app.command("move")
def columns_move(
    grid_id: GridIDArg,
    column_slug: Annotated[
        str, typer.Option("--column-slug", help="Slug of the first column to move.")
    ],
    position: Annotated[int, typer.Option("--position", help="Zero-based destination index.")],
    revision: RevisionOpt = None,
    columns_count: Annotated[
        int | None, typer.Option("--columns-count", help="How many consecutive columns to move.")
    ] = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Reorder columns in a grid (POST /grids/{id}/columns/move)."""
    body = ColumnsMove(
        revision=revision,
        column_slug=column_slug,
        position=position,
        columns_count=columns_count,
    )
    return wiki.grids.columns_move(grid_id, body=body)


@cells_app.command("update")
def cells_update(
    grid_id: GridIDArg,
    cells: Annotated[
        str,
        typer.Option(
            "--cells",
            help='Cells as JSON, e.g. \'[{"row_id":1,"column_slug":"name","value":"x"}]\'.',
        ),
    ],
    revision: RevisionOpt = None,
    *,
    wiki: WikiClient,
) -> CellsUpdateResult:
    """Set individual cell values in a grid (POST /grids/{id}/cells)."""
    body = CellsUpdate(revision=revision, cells=json.loads(cells))
    return wiki.grids.cells_update(grid_id, body=body)


@rows_app.command("update")
def rows_update(
    grid_id: GridIDArg,
    row_id: Annotated[str, typer.Argument(metavar="ROW_ID", help="Id of the row to update.")],
    revision: OptionalRevisionOpt = None,
    pinned: Annotated[
        bool | None, typer.Option("--pinned/--no-pinned", help="Pin or unpin the row.")
    ] = None,
    color: Annotated[
        str | None, values_option(BGColor, "--color", help="Row background colour.")
    ] = None,
    *,
    wiki: WikiClient,
) -> RowUpdateResult:
    """Pin or colour a row (POST /grids/{id}/rows/{row_id}; undocumented by Yandex)."""
    body = RowUpdate(
        revision=revision,
        pinned=pinned,
        color=color,
    )
    return wiki.grids.rows_update(grid_id, row_id, body=body)


@columns_app.command("suggest")
def columns_suggest(
    grid_id: GridIDArg,
    title: Annotated[
        str | None, typer.Option("--title", help="Title to turn into a slug and check.")
    ] = None,
    slug: Annotated[str | None, typer.Option("--slug", help="Slug to check.")] = None,
    *,
    wiki: WikiClient,
) -> ColumnSuggestion:
    """Check a column slug (POST /grids/{id}/columns/suggest; reads only; undocumented API)."""
    body = ColumnSuggest(title=title, slug=slug)
    return wiki.grids.columns_suggest(grid_id, body=body)


@columns_app.command("update")
def columns_update(
    grid_id: GridIDArg,
    column_slug: Annotated[
        str, typer.Argument(metavar="COLUMN_SLUG", help="Slug of the column to edit.")
    ],
    revision: OptionalRevisionOpt = None,
    title: Annotated[str | None, typer.Option("--title", help="New column header.")] = None,
    description: Annotated[
        str | None, typer.Option("--description", help="New description.")
    ] = None,
    required: Annotated[
        bool | None, typer.Option("--required/--no-required", help="Whether a value is mandatory.")
    ] = None,
    width: Annotated[int | None, typer.Option("--width", help="Column width.")] = None,
    width_units: Annotated[
        str | None, values_option(WidthUnits, "--width-units", help="Unit of --width.")
    ] = None,
    pinned: Annotated[
        str | None, values_option(ColumnPinType, "--pinned", help="The edge to pin the column to.")
    ] = None,
    color: Annotated[
        str | None, values_option(BGColor, "--color", help="Column background colour.")
    ] = None,
    select_options: Annotated[
        list[str] | None,
        typer.Option("--select-option", help="Allowed choice of a select column (repeatable)."),
    ] = None,
    *,
    wiki: WikiClient,
) -> ColumnUpdateResult:
    """Edit a column in place (POST /grids/{id}/column/{slug}; undocumented by Yandex).

    Only the options given change; the column type and slug cannot be edited.
    """
    body = ColumnUpdate(
        revision=revision,
        title=title,
        description=description,
        required=required,
        width=width,
        width_units=width_units,
        pinned=pinned,
        color=color,
        select_options=select_options,
    )
    return wiki.grids.columns_update(grid_id, column_slug, body=body)
