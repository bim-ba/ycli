"""DataLens collections FastMCP tools (reads and writes) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
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
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    GRANTS_ACCESS,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    All,
    Next,
    PermissionsInfo,
    app_config,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.models import (
    AccessBindingDelta,
    Operation,
    OrderField,
    SubjectWithBindings,
)
from ycli.yandex.models import ItemList, Listed, SortDirection

mcp = new_server("datalens-collections")

CollectionID = Annotated[str, Field(description="Collection id.")]


@mcp.tool(name="collections_get", annotations={**RO, "title": "Get DataLens collection"})
def get(
    collection_id: CollectionID,
    include_permissions_info: PermissionsInfo = None,
    client: DataLensClient = Depends(datalens_client),
) -> CollectionDetails:
    """One collection by id: its title, description and parent."""
    return client.collections.get(collection_id, include_permissions_info=include_permissions_info)


@mcp.tool(
    name="collections_list_by_ids", annotations={**RO, "title": "List DataLens collections by id"}
)
def list_by_ids(
    collection_ids: Annotated[list[str], Field(description="Collection ids.")],
    client: DataLensClient = Depends(datalens_client),
) -> ItemList[Collection]:
    """The collections with these ids; an id the caller cannot see is left out."""
    return client.collections.list_by_ids(collection_ids)


@mcp.tool(
    name="collections_content_list",
    annotations={**RO, "title": "List the content of a DataLens collection"},
)
def content_list(
    collection_id: Annotated[
        str | None, Field(description="Collection id; `null` lists the root.")
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max items to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    filter_string: Annotated[
        str | None, Field(description="Keep the items whose title has this text.")
    ] = None,
    order_field: Annotated[OrderField | None, Field(description="What to sort by.")] = None,
    order_direction: Annotated[SortDirection | None, Field(description="Sort direction.")] = None,
    only_my: Annotated[bool | None, Field(description="Keep only what the caller created.")] = None,
    mode: Annotated[ContentMode | None, Field(description="Which kinds of items to list.")] = None,
    include_permissions_info: PermissionsInfo = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[ContentItem]:
    """What a collection holds: collections, workbooks and entries, auto-paginated.

    Start here to find a workbook: list the root, then descend. Capped at the configured item
    cap unless ``limit`` is given.
    """
    return client.collections.content_list(
        collection_id,
        limit=config.http.tool_cap(limit, all_=all),
        next=next,
        filter_string=filter_string,
        order_field=order_field,
        order_direction=order_direction,
        only_my=only_my,
        mode=mode,
        include_permissions_info=include_permissions_info,
    ).collect()


@mcp.tool(
    name="collections_breadcrumbs_list",
    annotations={**RO, "title": "List the path of a DataLens collection"},
)
def breadcrumbs_list(
    collection_id: CollectionID,
    include_permissions_info: PermissionsInfo = None,
    client: DataLensClient = Depends(datalens_client),
) -> ItemList[CollectionBreadcrumb]:
    """The collections from the root down to this one."""
    return client.collections.breadcrumbs_list(
        collection_id, include_permissions_info=include_permissions_info
    )


@mcp.tool(
    name="collections_permissions_get_root",
    annotations={**RO, "title": "Get DataLens root permissions"},
)
def permissions_get_root(client: DataLensClient = Depends(datalens_client)) -> RootPermissions:
    """Whether the caller may create a collection and a workbook in the root."""
    return client.collections.permissions_get_root()


@mcp.tool(
    name="collections_access_bindings_list",
    annotations={**RO, "title": "List the roles on a DataLens collection"},
)
def access_bindings_list(
    collection_id: CollectionID,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max subjects to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    get_inherited_bindings: Annotated[
        bool | None, Field(description="Also list the roles inherited from above.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[SubjectWithBindings]:
    """Who has which role on a collection, auto-paginated."""
    return client.collections.access_bindings_list(
        collection_id,
        limit=config.http.tool_cap(limit, all_=all),
        next=next,
        get_inherited_bindings=get_inherited_bindings,
    ).collect()


ParentID = Annotated[
    str | None, Field(description="The collection to put it in; the root when left out.")
]


@mcp.tool(name="collections_create", annotations={**WRITE, "title": "Create DataLens collection"})
def create(
    title: Annotated[str, Field(description="Title of the collection.")],
    parent_id: ParentID = None,
    description: Annotated[str | None, Field(description="Description of the collection.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> CollectionCreated:
    """Create a collection in another one, or in the root when no parent is given."""
    return client.collections.create(title=title, parent_id=parent_id, description=description)


@mcp.tool(
    name="collections_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens collection"},
)
def update(
    collection_id: CollectionID,
    title: Annotated[str | None, Field(description="New title.")] = None,
    description: Annotated[str | None, Field(description="New description.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Collection:
    """Change a collection's title or description; what is not given stays as it is."""
    return client.collections.update(collection_id, title=title, description=description)


@mcp.tool(name="collections_move", annotations={**WRITE, "title": "Move DataLens collection"})
def move(
    collection_id: CollectionID,
    parent_id: ParentID = None,
    title: Annotated[str | None, Field(description="New title to give it on the way.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Collection:
    """Move a collection into another one, or into the root when no parent is given."""
    return client.collections.move(collection_id, parent_id=parent_id, title=title)


@mcp.tool(name="collections_move_bulk", annotations={**WRITE, "title": "Move DataLens collections"})
def move_bulk(
    collection_ids: Annotated[list[str], Field(description="Collection ids.")],
    parent_id: ParentID = None,
    client: DataLensClient = Depends(datalens_client),
) -> CollectionsMoved:
    """Move several collections into another one, or into the root when none is given.

    All or none: if one collection already lies in the destination, the API answers 409 and
    moves none of them.
    """
    return client.collections.move_bulk(collection_ids, parent_id=parent_id)


@mcp.tool(
    name="collections_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens collection"}
)
def delete(
    collection_id: CollectionID, client: DataLensClient = Depends(datalens_client)
) -> CollectionsDeleted:
    """Delete a collection with everything it holds: nested collections, workbooks, entries."""
    return client.collections.delete(collection_id)


@mcp.tool(
    name="collections_delete_bulk",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens collections"},
)
def delete_bulk(
    collection_ids: Annotated[list[str], Field(description="Collection ids.")],
    client: DataLensClient = Depends(datalens_client),
) -> CollectionsDeleted:
    """Delete several collections with everything they hold."""
    return client.collections.delete_bulk(collection_ids)


@mcp.tool(
    name="collections_access_bindings_update",
    annotations={**WRITE, "title": "Change the roles on a DataLens collection"},
    meta=GRANTS_ACCESS,
)
def access_bindings_update(
    collection_id: CollectionID,
    deltas: Annotated[
        list[AccessBindingDelta], Field(description="The roles to add (`ADD`) and remove.")
    ],
    client: DataLensClient = Depends(datalens_client),
) -> Operation:
    """Give or take away roles on a collection; the roles not named stay as they are."""
    return client.collections.access_bindings_update(collection_id, deltas=deltas)
