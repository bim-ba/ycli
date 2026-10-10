"""`datalens collections` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.collections.models import (
    Collection,
    CollectionBreadcrumb,
    CollectionCreated,
    CollectionDetails,
    CollectionsDeleted,
    CollectionsMoved,
    ContentItem,
    ContentMode,
    RootPermissions,
)
from ycli.yandex.datalens.models import (
    AccessBindingDelta,
    Operation,
    OrderField,
    SubjectWithBindings,
)
from ycli.yandex.datalens.typedefs import DeltaOption, PermissionsOption
from ycli.yandex.models import ItemList, SortDirection

app = typer.Typer(name="collections", help="DataLens collections.", no_args_is_help=True)

CollectionIDArg = Annotated[str, typer.Argument(metavar="COLLECTION_ID", help="Collection id.")]


@app.command()
def get(
    collection_id: CollectionIDArg,
    include_permissions_info: PermissionsOption = None,
    *,
    datalens: DataLensClient,
) -> CollectionDetails:
    """Print one collection."""
    return datalens.collections.get(
        collection_id, include_permissions_info=include_permissions_info
    )


@app.command("list-by-ids")
def list_by_ids(
    collection_ids: Annotated[
        list[str], typer.Argument(metavar="COLLECTION_ID...", help="Collection ids.")
    ],
    *,
    datalens: DataLensClient,
) -> ItemList[Collection]:
    """Print the collections with these ids."""
    return datalens.collections.list_by_ids(collection_ids)


@app.command("content-list")
def content_list(
    collection_id: Annotated[
        str | None,
        typer.Argument(metavar="[COLLECTION_ID]", help="Collection id; the root when left out."),
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    filter_string: Annotated[
        str | None, typer.Option("--filter-string", help="Keep the items whose title has this.")
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
    mode: Annotated[
        str | None, values_option(ContentMode, "--mode", help="Which kinds of items to list.")
    ] = None,
    include_permissions_info: PermissionsOption = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[ContentItem]:
    """List what a collection holds: collections, workbooks and entries (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.collections.content_list(
        collection_id,
        limit=cap,
        next=next_,
        filter_string=filter_string,
        order_field=order_field,
        order_direction=order_direction,
        only_my=only_my,
        mode=mode,
        include_permissions_info=include_permissions_info,
    )


@app.command("breadcrumbs-list")
def breadcrumbs_list(
    collection_id: CollectionIDArg,
    include_permissions_info: PermissionsOption = None,
    *,
    datalens: DataLensClient,
) -> ItemList[CollectionBreadcrumb]:
    """List the collections from the root down to this one."""
    return datalens.collections.breadcrumbs_list(
        collection_id, include_permissions_info=include_permissions_info
    )


@app.command("permissions-get-root")
def permissions_get_root(*, datalens: DataLensClient) -> RootPermissions:
    """Print what you may create in the root."""
    return datalens.collections.permissions_get_root()


@app.command("access-bindings-list")
def access_bindings_list(
    collection_id: CollectionIDArg,
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
    """List who has which role on a collection (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.collections.access_bindings_list(
        collection_id, limit=cap, next=next_, get_inherited_bindings=get_inherited_bindings
    )


ParentIDOption = Annotated[
    str | None,
    typer.Option("--parent-id", help="The collection to put it in; the root when left out."),
]


@app.command()
def create(
    title: Annotated[str, typer.Option("--title", help="Title of the collection.")],
    parent_id: ParentIDOption = None,
    description: Annotated[
        str | None, typer.Option("--description", help="Description of the collection.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> CollectionCreated:
    """Create a collection in --parent-id, or in the root."""
    return datalens.collections.create(title=title, parent_id=parent_id, description=description)


@app.command()
def update(
    collection_id: CollectionIDArg,
    title: Annotated[str | None, typer.Option("--title", help="New title.")] = None,
    description: Annotated[
        str | None, typer.Option("--description", help="New description.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> Collection:
    """Change a collection's title or description."""
    return datalens.collections.update(collection_id, title=title, description=description)


@app.command()
def move(
    collection_id: CollectionIDArg,
    parent_id: ParentIDOption = None,
    title: Annotated[
        str | None, typer.Option("--title", help="New title to give it on the way.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> Collection:
    """Move a collection into --parent-id, or into the root."""
    return datalens.collections.move(collection_id, parent_id=parent_id, title=title)


@app.command("move-bulk")
def move_bulk(
    collection_ids: Annotated[
        list[str], typer.Argument(metavar="COLLECTION_ID...", help="Collection ids.")
    ],
    parent_id: ParentIDOption = None,
    *,
    datalens: DataLensClient,
) -> CollectionsMoved:
    """Move several collections into --parent-id, or into the root."""
    return datalens.collections.move_bulk(collection_ids, parent_id=parent_id)


@app.command()
def delete(collection_id: CollectionIDArg, *, datalens: DataLensClient) -> CollectionsDeleted:
    """Delete a collection with everything it holds."""
    return datalens.collections.delete(collection_id)


@app.command("delete-bulk")
def delete_bulk(
    collection_ids: Annotated[
        list[str], typer.Argument(metavar="COLLECTION_ID...", help="Collection ids.")
    ],
    *,
    datalens: DataLensClient,
) -> CollectionsDeleted:
    """Delete several collections with everything they hold."""
    return datalens.collections.delete_bulk(collection_ids)


@app.command("access-bindings-update")
def access_bindings_update(
    collection_id: CollectionIDArg,
    deltas: DeltaOption,
    *,
    datalens: DataLensClient,
) -> Operation:
    """Give or take away roles on a collection; the roles not named stay as they are."""
    parsed = [AccessBindingDelta.model_validate_json(delta) for delta in deltas]
    return datalens.collections.access_bindings_update(collection_id, deltas=parsed)
