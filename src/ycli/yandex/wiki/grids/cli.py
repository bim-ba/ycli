"""`wiki grids` commands — dynamic-table CRUD plus rows/columns/cells and async clone.

Structured bodies (rows, columns, cells, default-sort) are passed as JSON strings and parsed
into the typed request models before sending. Every mutating call takes ``--revision`` (the
optimistic-lock token read off ``grids get``) except ``create``. ``clone`` is asynchronous:
``--wait`` (default) polls the ``operations`` resource to a terminal state.
"""

from __future__ import annotations

import json
import time
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.polling import poll
from ycli.yandex.wiki.grids.models import (
    CellsUpdate,
    ColumnsAdd,
    ColumnsMove,
    ColumnsRemove,
    GridClone,
    GridCreate,
    GridUpdate,
    PageIdentity,
    RowsAdd,
    RowsMove,
    RowsRemove,
)

app = typer.Typer(name="grids", help="Wiki dynamic tables (grids).", no_args_is_help=True)
rows_app = typer.Typer(name="rows", help="Grid rows.", no_args_is_help=True)
columns_app = typer.Typer(name="columns", help="Grid columns.", no_args_is_help=True)
cells_app = typer.Typer(name="cells", help="Grid cells.", no_args_is_help=True)


def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


app.callback()(_group)
rows_app.callback()(_group)
columns_app.callback()(_group)
cells_app.callback()(_group)
app.add_typer(rows_app)
app.add_typer(columns_app)
app.add_typer(cells_app)

GridIdArg = Annotated[str, typer.Argument(metavar="GRID_ID", help="Grid UUID.")]
RevisionOpt = Annotated[
    str, typer.Option("--revision", help="Current grid revision (optimistic lock).")
]
PositionOpt = Annotated[int | None, typer.Option("--position", help="Zero-based target index.")]


@app.command()
def get(
    ctx: typer.Context,
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
) -> None:
    """Fetch a grid by GRID_ID (GET /grids/{id}); read its revision to drive later writes."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.get(
            grid_id,
            fields=fields or None,
            row_filter=filter_ or None,
            only_cols=only_cols or None,
            only_rows=only_rows or None,
            revision=revision or None,
            sort=sort or None,
        ),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def create(
    ctx: typer.Context,
    title: Annotated[str, typer.Option(help="Title of the new grid.")],
    page_slug: Annotated[
        str, typer.Option("--page-slug", help="Target page slug, e.g. data/x.")
    ] = "",
    page_id: Annotated[int, typer.Option("--page-id", help="Target page numeric id.")] = 0,
) -> None:
    """Create a grid on a page (POST /grids). Pass one of --page-slug / --page-id."""
    if not page_id and not page_slug:
        raise typer.BadParameter("provide --page-slug or --page-id")
    page = PageIdentity(id=page_id) if page_id else PageIdentity(slug=page_slug)
    body = GridCreate(title=title, page=page).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.wiki.grids.create(body=body), app_ctx.strategy, app_ctx.console)


@app.command()
def update(
    ctx: typer.Context,
    grid_id: GridIdArg,
    revision: RevisionOpt,
    title: Annotated[str, typer.Option(help="New grid title.")] = "",
    default_sort: Annotated[
        str,
        typer.Option("--default-sort", help='New default sort as JSON, e.g. \'[{"slug":"a"}]\'.'),
    ] = "",
) -> None:
    """Rename / re-sort a grid (POST /grids/{id}; POST not PATCH)."""
    body = GridUpdate(
        revision=revision,
        title=title or None,
        default_sort=json.loads(default_sort) if default_sort else None,
    ).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.update(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def delete(ctx: typer.Context, grid_id: GridIdArg) -> None:
    """Delete a grid (DELETE /grids/{id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.wiki.grids.delete(grid_id), app_ctx.strategy, app_ctx.console)


@app.command()
def clone(
    ctx: typer.Context,
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
) -> None:
    """Copy a grid onto another page (POST /grids/{id}/clone; async). --wait polls to completion."""
    body = GridClone(target=target, title=title or None, with_data=with_data).model_dump(
        exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    operation = app_ctx.wiki.grids.clone(grid_id, body=body)
    if wait and operation.operation is not None and operation.operation.id is not None:
        task_id = operation.operation.id
        status = poll(
            lambda: app_ctx.wiki.operations.gridclone_get(task_id),
            lambda state: state.is_terminal,
            sleep=lambda seconds: time.sleep(seconds),
        )
        Serializer.serialize(status, app_ctx.strategy, app_ctx.console)
    else:
        Serializer.serialize(operation, app_ctx.strategy, app_ctx.console)


@rows_app.command("add")
def rows_add(
    ctx: typer.Context,
    grid_id: GridIdArg,
    revision: RevisionOpt,
    rows: Annotated[
        str, typer.Option("--rows", help='Rows as JSON, e.g. \'[{"name":"x"}]\' (slug→value).')
    ],
    position: PositionOpt = None,
    after_row_id: Annotated[
        str, typer.Option("--after-row-id", help="Insert after this row id.")
    ] = "",
) -> None:
    """Insert rows into a grid (POST /grids/{id}/rows)."""
    body = RowsAdd(
        revision=revision,
        rows=json.loads(rows),
        position=position,
        after_row_id=after_row_id or None,
    ).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.add_rows(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )


@rows_app.command("remove")
def rows_remove(
    ctx: typer.Context,
    grid_id: GridIdArg,
    revision: RevisionOpt,
    row_id: Annotated[list[str], typer.Option("--row-id", help="Row id to delete (repeatable).")],
) -> None:
    """Delete rows from a grid by id (DELETE /grids/{id}/rows)."""
    body = RowsRemove(revision=revision, row_ids=row_id).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.remove_rows(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )


@rows_app.command("move")
def rows_move(
    ctx: typer.Context,
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
) -> None:
    """Reorder rows in a grid (POST /grids/{id}/rows/move)."""
    body = RowsMove(
        revision=revision,
        row_id=row_id or None,
        after_row_id=after_row_id or None,
        position=position,
        rows_count=rows_count,
    ).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.move_rows(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )


@columns_app.command("add")
def columns_add(
    ctx: typer.Context,
    grid_id: GridIdArg,
    revision: RevisionOpt,
    columns: Annotated[
        str,
        typer.Option(
            "--columns", help='Columns as JSON, e.g. \'[{"title":"C","type":"string"}]\'.'
        ),
    ],
    position: PositionOpt = None,
) -> None:
    """Add columns to a grid (POST /grids/{id}/columns)."""
    body = ColumnsAdd(revision=revision, columns=json.loads(columns), position=position).model_dump(
        exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.add_columns(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )


@columns_app.command("remove")
def columns_remove(
    ctx: typer.Context,
    grid_id: GridIdArg,
    revision: RevisionOpt,
    column_slug: Annotated[
        list[str], typer.Option("--column-slug", help="Column slug to delete (repeatable).")
    ],
) -> None:
    """Delete columns from a grid by slug (DELETE /grids/{id}/columns)."""
    body = ColumnsRemove(revision=revision, column_slugs=column_slug).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.remove_columns(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )


@columns_app.command("move")
def columns_move(
    ctx: typer.Context,
    grid_id: GridIdArg,
    revision: RevisionOpt,
    column_slug: Annotated[
        str, typer.Option("--column-slug", help="Slug of the first column to move.")
    ] = "",
    position: PositionOpt = None,
    columns_count: Annotated[
        int | None, typer.Option("--columns-count", help="How many consecutive columns to move.")
    ] = None,
) -> None:
    """Reorder columns in a grid (POST /grids/{id}/columns/move)."""
    body = ColumnsMove(
        revision=revision,
        column_slug=column_slug or None,
        position=position,
        columns_count=columns_count,
    ).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.move_columns(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )


@cells_app.command("update")
def cells_update(
    ctx: typer.Context,
    grid_id: GridIdArg,
    revision: RevisionOpt,
    cells: Annotated[
        str,
        typer.Option(
            "--cells",
            help='Cells as JSON, e.g. \'[{"row_id":1,"column_slug":"name","value":"x"}]\'.',
        ),
    ],
) -> None:
    """Set individual cell values in a grid (POST /grids/{id}/cells)."""
    body = CellsUpdate(revision=revision, cells=json.loads(cells)).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.grids.update_cells(grid_id, body=body), app_ctx.strategy, app_ctx.console
    )
