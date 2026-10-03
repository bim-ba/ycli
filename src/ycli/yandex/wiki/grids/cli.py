"""`wiki grids` commands — dynamic-table CRUD plus rows/columns/cells and async clone.

Structured bodies (rows, columns, cells, default-sort) are passed as JSON strings and parsed
into the typed request models before sending. Every mutating call takes ``--revision`` (the
optimistic-lock token read off ``grids get``) except ``create``. ``clone`` is asynchronous:
``--wait`` (default) polls the ``operations`` resource to a terminal state.
"""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.progress import wait_for
from ycli.yandex.models import Ack
from ycli.yandex.wiki.client import WikiClient
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
from ycli.yandex.wiki.models import AsyncOperation, PageIdentity
from ycli.yandex.wiki.operations.models import GridCloneOperationStatus

app = typer.Typer(name="grids", help="Wiki dynamic tables (grids).", no_args_is_help=True)
rows_app = typer.Typer(name="rows", help="Grid rows.", no_args_is_help=True)
columns_app = typer.Typer(name="columns", help="Grid columns.", no_args_is_help=True)
cells_app = typer.Typer(name="cells", help="Grid cells.", no_args_is_help=True)


app.add_typer(rows_app)
app.add_typer(columns_app)
app.add_typer(cells_app)

GridIdArg = Annotated[str, typer.Argument(metavar="GRID_ID", help="Grid UUID.")]
RevisionOpt = Annotated[
    str, typer.Option("--revision", help="Current grid revision (optimistic lock).")
]
OptionalRevisionOpt = Annotated[
    str, typer.Option("--revision", help="Grid revision (this endpoint does not enforce it).")
]
PositionOpt = Annotated[int | None, typer.Option("--position", help="Zero-based target index.")]


@app.command()
def get(
    grid_id: GridIdArg,
    fields: Annotated[
        str, typer.Option(help="Extra blocks, e.g. attributes,user_permissions.")
    ] = "",
    filter_: Annotated[
        str, typer.Option("--filter", help="Row filter expr, e.g. [slug] ~ wiki.")
    ] = "",
    only_cols: Annotated[
        str, typer.Option("--only-cols", help="Only these column slugs (CSV).")
    ] = "",
    only_rows: Annotated[str, typer.Option("--only-rows", help="Only these row ids (CSV).")] = "",
    revision: Annotated[str, typer.Option("--revision", help="Load a historical revision.")] = "",
    sort: Annotated[str, typer.Option(help="Row sort, e.g. slug,-slug2.")] = "",
    *,
    wiki: WikiClient,
) -> Grid:
    """Fetch a grid by GRID_ID (GET /grids/{id}); read its revision to drive later writes."""
    return wiki.grids.get(
        grid_id,
        fields=fields or None,
        row_filter=filter_ or None,
        only_cols=only_cols or None,
        only_rows=only_rows or None,
        revision=revision or None,
        sort=sort or None,
    )


@app.command()
def create(
    title: Annotated[str, typer.Option(help="Title of the new grid.")],
    page_slug: Annotated[
        str, typer.Option("--page-slug", help="Target page slug, e.g. data/x.")
    ] = "",
    page_id: Annotated[int, typer.Option("--page-id", help="Target page numeric id.")] = 0,
    *,
    wiki: WikiClient,
) -> Grid:
    """Create a grid on a page (POST /grids). Pass one of --page-slug / --page-id."""
    if not page_id and not page_slug:
        raise typer.BadParameter("provide --page-slug or --page-id")
    page = PageIdentity(id=page_id) if page_id else PageIdentity(slug=page_slug)
    body = GridCreate(title=title, page=page).model_dump(exclude_none=True)
    return wiki.grids.create(body=body)


@app.command()
def update(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    title: Annotated[str, typer.Option(help="New grid title.")] = "",
    default_sort: Annotated[
        str,
        typer.Option(
            "--default-sort",
            help="New default sort as JSON in the write shape "
            '\'[{"<column_slug>": "asc"|"desc"}]\', e.g. \'[{"priority": "desc"}]\'.',
        ),
    ] = "",
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Rename / re-sort a grid (POST /grids/{id}; POST not PATCH).

    ``--default-sort`` takes the API's write shape (column slug → direction mappings), not the
    ``{slug, title, direction}`` read shape that ``grids get`` returns.
    """
    body = GridUpdate(
        revision=revision,
        title=title or None,
        default_sort=json.loads(default_sort) if default_sort else None,
    ).model_dump(exclude_none=True)
    return wiki.grids.update(grid_id, body=body)


@app.command()
def delete(grid_id: GridIdArg, *, wiki: WikiClient) -> Ack:
    """Delete a grid (DELETE /grids/{id})."""
    return wiki.grids.delete(grid_id)


@app.command()
def clone(
    grid_id: GridIdArg,
    target: Annotated[
        str, typer.Option("--target", help="Destination page slug (created if absent).")
    ],
    title: Annotated[str, typer.Option(help="Title of the copy, if renaming.")] = "",
    with_data: Annotated[
        bool, typer.Option("--with-data", help="Copy the rows too, not just the structure.")
    ] = False,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    wiki: WikiClient,
) -> AsyncOperation | GridCloneOperationStatus:
    """Copy a grid onto another page (POST /grids/{id}/clone; async). --wait polls to completion."""
    body = GridClone(target=target, title=title or None, with_data=with_data).model_dump(
        exclude_none=True
    )
    operation = wiki.grids.clone(grid_id, body=body)
    if wait and operation.operation is not None and operation.operation.id is not None:
        task_id = operation.operation.id
        status = wait_for(
            lambda: wiki.operations.gridclone_get(task_id),
            lambda state: state.is_terminal,
            message="Waiting for grid clone…",
        )
        return status
    return operation


@rows_app.command("add")
def rows_add(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    rows: Annotated[
        str, typer.Option("--rows", help='Rows as JSON, e.g. \'[{"name":"x"}]\' (slug→value).')
    ],
    position: PositionOpt = None,
    after_row_id: Annotated[
        str, typer.Option("--after-row-id", help="Insert after this row id.")
    ] = "",
    *,
    wiki: WikiClient,
) -> RowsAddResult:
    """Insert rows into a grid (POST /grids/{id}/rows)."""
    body = RowsAdd(
        revision=revision,
        rows=json.loads(rows),
        position=position,
        after_row_id=after_row_id or None,
    ).model_dump(exclude_none=True)
    return wiki.grids.add_rows(grid_id, body=body)


@rows_app.command("remove")
def rows_remove(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    row_id: Annotated[list[str], typer.Option("--row-id", help="Row id to delete (repeatable).")],
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Delete rows from a grid by id (DELETE /grids/{id}/rows)."""
    body = RowsRemove(revision=revision, row_ids=row_id).model_dump(exclude_none=True)
    return wiki.grids.remove_rows(grid_id, body=body)


@rows_app.command("move")
def rows_move(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    row_id: Annotated[str, typer.Option("--row-id", help="Id of the first row to move.")] = "",
    after_row_id: Annotated[
        str, typer.Option("--after-row-id", help="Move to just after this row id.")
    ] = "",
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
        row_id=row_id or None,
        after_row_id=after_row_id or None,
        position=position,
        rows_count=rows_count,
    ).model_dump(exclude_none=True)
    return wiki.grids.move_rows(grid_id, body=body)


@columns_app.command("add")
def columns_add(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    columns: Annotated[
        str,
        typer.Option(
            "--columns",
            help='Columns as JSON, e.g. \'[{"title":"C","type":"string"}]\' '
            "(slug derived from the title when omitted).",
        ),
    ],
    position: PositionOpt = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Add columns to a grid (POST /grids/{id}/columns).

    The API requires a ``slug`` on every column; a column without one gets a slug derived from
    its title (lowercased, non-alphanumeric runs collapsed to ``_``).
    """
    body = ColumnsAdd(revision=revision, columns=json.loads(columns), position=position).model_dump(
        exclude_none=True
    )
    return wiki.grids.add_columns(grid_id, body=body)


@columns_app.command("remove")
def columns_remove(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    column_slug: Annotated[
        list[str], typer.Option("--column-slug", help="Column slug to delete (repeatable).")
    ],
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Delete columns from a grid by slug (DELETE /grids/{id}/columns)."""
    body = ColumnsRemove(revision=revision, column_slugs=column_slug).model_dump(exclude_none=True)
    return wiki.grids.remove_columns(grid_id, body=body)


@columns_app.command("move")
def columns_move(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    column_slug: Annotated[
        str, typer.Option("--column-slug", help="Slug of the first column to move.")
    ] = "",
    position: PositionOpt = None,
    columns_count: Annotated[
        int | None, typer.Option("--columns-count", help="How many consecutive columns to move.")
    ] = None,
    *,
    wiki: WikiClient,
) -> RevisionResult:
    """Reorder columns in a grid (POST /grids/{id}/columns/move)."""
    body = ColumnsMove(
        revision=revision,
        column_slug=column_slug or None,
        position=position,
        columns_count=columns_count,
    ).model_dump(exclude_none=True)
    return wiki.grids.move_columns(grid_id, body=body)


@cells_app.command("update")
def cells_update(
    grid_id: GridIdArg,
    revision: RevisionOpt,
    cells: Annotated[
        str,
        typer.Option(
            "--cells",
            help='Cells as JSON, e.g. \'[{"row_id":1,"column_slug":"name","value":"x"}]\'.',
        ),
    ],
    *,
    wiki: WikiClient,
) -> CellsUpdateResult:
    """Set individual cell values in a grid (POST /grids/{id}/cells)."""
    body = CellsUpdate(revision=revision, cells=json.loads(cells)).model_dump(exclude_none=True)
    return wiki.grids.update_cells(grid_id, body=body)


@rows_app.command("update")
def rows_update(
    grid_id: GridIdArg,
    row_id: Annotated[str, typer.Argument(metavar="ROW_ID", help="Id of the row to update.")],
    revision: OptionalRevisionOpt = "",
    pinned: Annotated[
        bool | None, typer.Option("--pinned/--no-pinned", help="Pin or unpin the row.")
    ] = None,
    color: Annotated[str, typer.Option("--color", help="Row background colour, e.g. mint.")] = "",
    *,
    wiki: WikiClient,
) -> RowUpdateResult:
    """Pin or colour a row (POST /grids/{id}/rows/{row_id}; undocumented by Yandex)."""
    body = RowUpdate(
        revision=revision or None,
        pinned=pinned,
        color=color or None,  # ty: ignore[invalid-argument-type]  # pydantic validates the colour literal
    ).model_dump(exclude_none=True)
    return wiki.grids.update_row(grid_id, row_id, body=body)


@columns_app.command("suggest")
def columns_suggest(
    grid_id: GridIdArg,
    title: Annotated[
        str, typer.Option("--title", help="Title to turn into a slug and check.")
    ] = "",
    slug: Annotated[str, typer.Option("--slug", help="Slug to check.")] = "",
    *,
    wiki: WikiClient,
) -> ColumnSuggestion:
    """Check a column slug (POST /grids/{id}/columns/suggest; reads only; undocumented API)."""
    body = ColumnSuggest(title=title or None, slug=slug or None).model_dump(exclude_none=True)
    return wiki.grids.suggest_column(grid_id, body=body)


@columns_app.command("update")
def columns_update(
    grid_id: GridIdArg,
    column_slug: Annotated[
        str, typer.Argument(metavar="COLUMN_SLUG", help="Slug of the column to edit.")
    ],
    revision: OptionalRevisionOpt = "",
    title: Annotated[str, typer.Option("--title", help="New column header.")] = "",
    description: Annotated[str, typer.Option("--description", help="New description.")] = "",
    required: Annotated[
        bool | None, typer.Option("--required/--no-required", help="Whether a value is mandatory.")
    ] = None,
    width: Annotated[int | None, typer.Option("--width", help="Column width.")] = None,
    width_units: Annotated[str, typer.Option("--width-units", help="% or px.")] = "",
    pinned: Annotated[str, typer.Option("--pinned", help="left or right.")] = "",
    color: Annotated[str, typer.Option("--color", help="Column background colour.")] = "",
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
        revision=revision or None,
        title=title or None,
        description=description or None,
        required=required,
        width=width,
        width_units=width_units or None,  # ty: ignore[invalid-argument-type]  # pydantic validates the unit literal
        pinned=pinned or None,  # ty: ignore[invalid-argument-type]  # pydantic validates the edge literal
        color=color or None,  # ty: ignore[invalid-argument-type]  # pydantic validates the colour literal
        select_options=select_options,
    ).model_dump(exclude_none=True)
    return wiki.grids.update_column(grid_id, column_slug, body=body)
