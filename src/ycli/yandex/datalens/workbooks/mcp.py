"""DataLens workbooks FastMCP tools (reads and writes) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    PermissionsInfo,
    app_config,
    datalens_client,
)
from ycli.yandex.datalens.models import (
    AccessBindingDelta,
    Operation,
    OrderField,
    SubjectWithBindings,
)
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

mcp = FastMCP("datalens-workbooks")

WorkbookID = Annotated[str, Field(description="Workbook id.")]


@mcp.tool(name="workbooks_get", annotations={**RO, "title": "Get DataLens workbook"})
def get(
    workbook_id: WorkbookID,
    include_permissions_info: PermissionsInfo = None,
    client: DataLensClient = Depends(datalens_client),
) -> WorkbookDetails:
    """One workbook by id: its title, description and collection."""
    return client.workbooks.get(workbook_id, include_permissions_info=include_permissions_info)


@mcp.tool(name="workbooks_list", annotations={**RO, "title": "List DataLens workbooks"})
def list_(
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max workbooks to return; {LIMIT_CAP}")
    ] = None,
    collection_id: Annotated[
        str | None, Field(description="Collection to list; the root when left out.")
    ] = None,
    filter_string: Annotated[
        str | None, Field(description="Keep the workbooks whose title has this text.")
    ] = None,
    order_field: Annotated[OrderField | None, Field(description="What to sort by.")] = None,
    order_direction: Annotated[SortDirection | None, Field(description="Sort direction.")] = None,
    only_my: Annotated[bool | None, Field(description="Keep only what the caller created.")] = None,
    include_permissions_info: PermissionsInfo = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[WorkbookListed]:
    """The workbooks of one collection (the root by default), auto-paginated.

    It does not descend into nested collections: ``collections_content_list`` shows what a
    collection holds. Capped at the configured item cap unless ``limit`` is given.
    """
    return client.workbooks.list(
        limit=config.http.cap(limit),
        collection_id=collection_id,
        filter_string=filter_string,
        order_field=order_field,
        order_direction=order_direction,
        only_my=only_my,
        include_permissions_info=include_permissions_info,
    )


@mcp.tool(
    name="workbooks_list_by_ids", annotations={**RO, "title": "List DataLens workbooks by id"}
)
def list_by_ids(
    workbook_ids: Annotated[list[str], Field(description="Workbook ids.")],
    client: DataLensClient = Depends(datalens_client),
) -> ItemList[Workbook]:
    """The workbooks with these ids; an id the caller cannot see is left out."""
    return client.workbooks.list_by_ids(workbook_ids)


@mcp.tool(
    name="workbooks_access_bindings_list",
    annotations={**RO, "title": "List the roles on a DataLens workbook"},
)
def access_bindings_list(
    workbook_id: WorkbookID,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max subjects to return; {LIMIT_CAP}")
    ] = None,
    get_inherited_bindings: Annotated[
        bool | None, Field(description="Also list the roles inherited from above.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[SubjectWithBindings]:
    """Who has which role on a workbook, auto-paginated."""
    return client.workbooks.access_bindings_list(
        workbook_id,
        limit=config.http.cap(limit),
        get_inherited_bindings=get_inherited_bindings,
    )


IntoCollection = Annotated[
    str | None, Field(description="The collection to put the workbook in; the root when left out.")
]
WorkbookIDs = Annotated[list[str], Field(description="Workbook ids.")]


@mcp.tool(
    name="workbooks_entries_list",
    annotations={**RO, "title": "List the entries of a DataLens workbook"},
)
def entries_list(
    workbook_id: WorkbookID,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max entries to return; {LIMIT_CAP}")
    ] = None,
    include_permissions_info: PermissionsInfo = None,
    only_my: Annotated[bool | None, Field(description="Keep only what the caller created.")] = None,
    created_by: Annotated[
        str | None, Field(description="Keep only what this user created.")
    ] = None,
    scope: Annotated[
        list[EntryScope] | None, Field(description="Keep only these kinds of entries.")
    ] = None,
    order_by: Annotated[
        EntriesOrder | None, Field(description="What to sort by and in which direction.")
    ] = None,
    filters: Annotated[
        EntriesFilters | None, Field(description="Keep the entries whose name has a text.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[WorkbookEntry]:
    """What a workbook holds: connections, datasets, charts and dashboards, auto-paginated.

    ``scope`` says the kind of each entry; its id opens it with the tools of that kind. Capped
    at the configured item cap unless ``limit`` is given.
    """
    return client.workbooks.entries_list(
        workbook_id,
        limit=config.http.cap(limit),
        include_permissions_info=include_permissions_info,
        only_my=only_my,
        created_by=created_by,
        scope=scope,
        order_by=order_by,
        filters=filters,
    )


@mcp.tool(name="workbooks_create", annotations={**WRITE, "title": "Create DataLens workbook"})
def create(
    title: Annotated[str, Field(description="Title of the workbook.")],
    collection_id: IntoCollection = None,
    description: Annotated[str | None, Field(description="Description of the workbook.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> WorkbookCreated:
    """Create a workbook in a collection, or in the root when no collection is given."""
    return client.workbooks.create(
        title=title, collection_id=collection_id, description=description
    )


@mcp.tool(
    name="workbooks_update", annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens workbook"}
)
def update(
    workbook_id: WorkbookID,
    title: Annotated[str | None, Field(description="New title.")] = None,
    description: Annotated[str | None, Field(description="New description.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Workbook:
    """Change a workbook's title or description; what is not given stays as it is."""
    return client.workbooks.update(workbook_id, title=title, description=description)


@mcp.tool(name="workbooks_move", annotations={**WRITE, "title": "Move DataLens workbook"})
def move(
    workbook_id: WorkbookID,
    collection_id: IntoCollection = None,
    title: Annotated[str | None, Field(description="New title to give it on the way.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Workbook:
    """Move a workbook into a collection, or into the root when no collection is given."""
    return client.workbooks.move(workbook_id, collection_id=collection_id, title=title)


@mcp.tool(name="workbooks_move_bulk", annotations={**WRITE, "title": "Move DataLens workbooks"})
def move_bulk(
    workbook_ids: WorkbookIDs,
    collection_id: IntoCollection = None,
    client: DataLensClient = Depends(datalens_client),
) -> WorkbooksMoved:
    """Move several workbooks into a collection, or into the root when none is given.

    All or none: if one workbook already lies in the destination, the API answers 409 and
    moves none of them.
    """
    return client.workbooks.move_bulk(workbook_ids, collection_id=collection_id)


@mcp.tool(name="workbooks_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens workbook"})
def delete(workbook_id: WorkbookID, client: DataLensClient = Depends(datalens_client)) -> Workbook:
    """Delete a workbook with everything it holds: connections, datasets, charts, dashboards."""
    return client.workbooks.delete(workbook_id)


@mcp.tool(
    name="workbooks_delete_bulk",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens workbooks"},
)
def delete_bulk(
    workbook_ids: WorkbookIDs, client: DataLensClient = Depends(datalens_client)
) -> WorkbooksDeleted:
    """Delete several workbooks with everything they hold."""
    return client.workbooks.delete_bulk(workbook_ids)


@mcp.tool(
    name="workbooks_access_bindings_update",
    annotations={**WRITE, "title": "Change the roles on a DataLens workbook"},
)
def access_bindings_update(
    workbook_id: WorkbookID,
    deltas: Annotated[
        list[AccessBindingDelta], Field(description="The roles to add (`ADD`) and remove.")
    ],
    client: DataLensClient = Depends(datalens_client),
) -> Operation:
    """Give or take away roles on a workbook; the roles not named stay as they are."""
    return client.workbooks.access_bindings_update(workbook_id, deltas=deltas)
