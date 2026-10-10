"""`datalens workbooks` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import (
    AccessBindingDelta,
    Operation,
    OrderField,
    SubjectWithBindings,
)
from ycli.yandex.datalens.typedefs import DeltaOption, PermissionsOption
from ycli.yandex.datalens.workbooks.models import (
    EntriesFilters,
    EntriesOrder,
    EntryScope,
    Workbook,
    WorkbookCreated,
    WorkbookDetails,
    WorkbookEntry,
    WorkbookListed,
    WorkbooksDeleted,
    WorkbooksMoved,
)
from ycli.yandex.models import ItemList, SortDirection

app = typer.Typer(name="workbooks", help="DataLens workbooks.", no_args_is_help=True)

WorkbookIDArg = Annotated[str, typer.Argument(metavar="WORKBOOK_ID", help="Workbook id.")]


@app.command()
def get(
    workbook_id: WorkbookIDArg,
    include_permissions_info: PermissionsOption = None,
    *,
    datalens: DataLensClient,
) -> WorkbookDetails:
    """Print one workbook."""
    return datalens.workbooks.get(workbook_id, include_permissions_info=include_permissions_info)


@app.command("list")
def list_(
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    collection_id: Annotated[
        str | None,
        typer.Option("--collection-id", help="Collection to list; the root when left out."),
    ] = None,
    filter_string: Annotated[
        str | None, typer.Option("--filter-string", help="Keep the titles that have this.")
    ] = None,
    order_field: Annotated[
        str | None, values_option(OrderField, "--order-field", help="What to sort by.")
    ] = None,
    order_direction: Annotated[
        str | None, values_option(SortDirection, "--order-direction", help="Sort direction.")
    ] = None,
    only_my: Annotated[
        bool | None, typer.Option("--only-my/--no-only-my", help="Keep only what you created.")
    ] = None,
    include_permissions_info: PermissionsOption = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[WorkbookListed]:
    """List the workbooks of a collection (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.workbooks.list(
        limit=cap,
        next=next_,
        collection_id=collection_id,
        filter_string=filter_string,
        order_field=order_field,
        order_direction=order_direction,
        only_my=only_my,
        include_permissions_info=include_permissions_info,
    )


@app.command("list-by-ids")
def list_by_ids(
    workbook_ids: Annotated[
        list[str], typer.Argument(metavar="WORKBOOK_ID...", help="Workbook ids.")
    ],
    *,
    datalens: DataLensClient,
) -> ItemList[Workbook]:
    """Print the workbooks with these ids."""
    return datalens.workbooks.list_by_ids(workbook_ids)


@app.command("access-bindings-list")
def access_bindings_list(
    workbook_id: WorkbookIDArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    get_inherited_bindings: Annotated[
        bool | None,
        typer.Option(
            "--get-inherited-bindings/--no-get-inherited-bindings",
            help="Also list the inherited roles.",
        ),
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[SubjectWithBindings]:
    """List who has which role on a workbook (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.workbooks.access_bindings_list(
        workbook_id, limit=cap, next=next_, get_inherited_bindings=get_inherited_bindings
    )


CollectionIDOption = Annotated[
    str | None,
    typer.Option("--collection-id", help="The collection to put it in; the root when left out."),
]
WorkbookIDsArg = Annotated[
    list[str], typer.Argument(metavar="WORKBOOK_ID...", help="Workbook ids.")
]


@app.command("entries-list")
def entries_list(
    workbook_id: WorkbookIDArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    include_permissions_info: PermissionsOption = None,
    only_my: Annotated[
        bool | None, typer.Option("--only-my/--no-only-my", help="Keep only what you created.")
    ] = None,
    created_by: Annotated[
        str | None, typer.Option("--created-by", help="Keep only what this user created.")
    ] = None,
    scope: Annotated[
        list[str] | None,
        values_option(EntryScope, "--scope", help="Keep only this kind of entry (repeatable)."),
    ] = None,
    order_by: Annotated[
        str | None,
        typer.Option(
            "--order-by",
            help='What to sort by, as a JSON object: {"field": "name", "direction": "asc"}.',
        ),
    ] = None,
    filters: Annotated[
        str | None,
        typer.Option("--filters", help='A filter, as a JSON object: {"name": "sales"}.'),
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[WorkbookEntry]:
    """List what a workbook holds: connections, datasets, charts, dashboards (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.workbooks.entries_list(
        workbook_id,
        limit=cap,
        next=next_,
        include_permissions_info=include_permissions_info,
        only_my=only_my,
        created_by=created_by,
        scope=scope,
        order_by=None if order_by is None else EntriesOrder.model_validate_json(order_by),
        filters=None if filters is None else EntriesFilters.model_validate_json(filters),
    )


@app.command()
def create(
    title: Annotated[str, typer.Option("--title", help="Title of the workbook.")],
    collection_id: CollectionIDOption = None,
    description: Annotated[
        str | None, typer.Option("--description", help="Description of the workbook.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> WorkbookCreated:
    """Create a workbook in --collection-id, or in the root."""
    return datalens.workbooks.create(
        title=title, collection_id=collection_id, description=description
    )


@app.command()
def update(
    workbook_id: WorkbookIDArg,
    title: Annotated[str | None, typer.Option("--title", help="New title.")] = None,
    description: Annotated[
        str | None, typer.Option("--description", help="New description.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> Workbook:
    """Change a workbook's title or description."""
    return datalens.workbooks.update(workbook_id, title=title, description=description)


@app.command()
def move(
    workbook_id: WorkbookIDArg,
    collection_id: CollectionIDOption = None,
    title: Annotated[
        str | None, typer.Option("--title", help="New title to give it on the way.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> Workbook:
    """Move a workbook into --collection-id, or into the root."""
    return datalens.workbooks.move(workbook_id, collection_id=collection_id, title=title)


@app.command("move-bulk")
def move_bulk(
    workbook_ids: WorkbookIDsArg,
    collection_id: CollectionIDOption = None,
    *,
    datalens: DataLensClient,
) -> WorkbooksMoved:
    """Move several workbooks into --collection-id, or into the root."""
    return datalens.workbooks.move_bulk(workbook_ids, collection_id=collection_id)


@app.command()
def delete(workbook_id: WorkbookIDArg, *, datalens: DataLensClient) -> Workbook:
    """Delete a workbook with everything it holds."""
    return datalens.workbooks.delete(workbook_id)


@app.command("delete-bulk")
def delete_bulk(workbook_ids: WorkbookIDsArg, *, datalens: DataLensClient) -> WorkbooksDeleted:
    """Delete several workbooks with everything they hold."""
    return datalens.workbooks.delete_bulk(workbook_ids)


@app.command("access-bindings-update")
def access_bindings_update(
    workbook_id: WorkbookIDArg, deltas: DeltaOption, *, datalens: DataLensClient
) -> Operation:
    """Give or take away roles on a workbook; the roles not named stay as they are."""
    parsed = [AccessBindingDelta.model_validate_json(delta) for delta in deltas]
    return datalens.workbooks.access_bindings_update(workbook_id, deltas=parsed)
