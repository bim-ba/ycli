"""DataLens entries FastMCP tools (reads and one write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    LIMIT_CAP,
    RO,
    WRITE_IDEMPOTENT,
    All,
    EntryID,
    Next,
    PermissionsInfo,
    app_config,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.entries.models import (
    EntriesPermissions,
    Entry,
    ListFilters,
    ListOrder,
    Relation,
    Renamed,
    Revision,
)
from ycli.yandex.datalens.models import EntryScope
from ycli.yandex.models import ItemList, Listed

mcp = new_server("datalens-entries")

EntryIDs = Annotated[list[str], Field(description="Entry ids.")]


@mcp.tool(name="entries_list", annotations={**RO, "title": "Find DataLens entries"})
def list_(
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max entries to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    ids: Annotated[list[str] | None, Field(description="Keep the entries with these ids.")] = None,
    scope: Annotated[EntryScope | None, Field(description="Keep one kind of entry.")] = None,
    scopes: Annotated[
        list[EntryScope] | None, Field(description="Keep several kinds of entries.")
    ] = None,
    type: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None, Field(description="Keep these types of entries.")
    ] = None,
    created_by: Annotated[
        list[str] | None, Field(description="Keep what these users created.")
    ] = None,
    order_by: Annotated[
        ListOrder | None, Field(description="What to sort by and in which direction.")
    ] = None,
    exclude_locked: Annotated[
        bool | None, Field(description="Leave out the entries the caller may not read.")
    ] = None,
    include_links: Annotated[
        bool | None, Field(description="Also say what each entry is linked to.")
    ] = None,
    filters: Annotated[
        ListFilters | None, Field(description="Keep the entries whose name has a text.")
    ] = None,
    include_permissions_info: PermissionsInfo = None,
    ignore_workbook_entries: Annotated[
        bool | None, Field(description="Leave out the entries that lie in workbooks.")
    ] = None,
    ignore_shared_entries: Annotated[
        bool | None, Field(description="Leave out the shared entries.")
    ] = None,
    include_data: Annotated[
        bool | None, Field(description="Also give the content of each entry (large).")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Entry]:
    """Entries across the whole organization: dashboards, charts, datasets, connections.

    The API requires one of ``scope``, ``scopes`` and ``ids``. An entry the caller may not read
    comes with ``isLocked`` set and little else. Auto-paginated; capped at the configured item
    cap unless ``limit`` is given.
    """
    return client.entries.list(
        limit=config.http.cap(limit, all_=all),
        next=next,
        ids=ids,
        scope=scope,
        scopes=scopes,
        type=type,
        created_by=created_by,
        order_by=order_by,
        exclude_locked=exclude_locked,
        include_links=include_links,
        filters=filters,
        include_permissions_info=include_permissions_info,
        ignore_workbook_entries=ignore_workbook_entries,
        ignore_shared_entries=ignore_shared_entries,
        include_data=include_data,
    ).collect()


@mcp.tool(
    name="entries_relations_list",
    annotations={**RO, "title": "List what DataLens entries use or are used by"},
)
def relations_list(
    entry_ids: EntryIDs,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max relations to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    link_direction: Annotated[
        str | None,
        Field(description="`from`: what the entries use; `to`: what uses them."),
    ] = None,
    include_permissions_info: PermissionsInfo = None,
    scope: Annotated[
        EntryScope | None, Field(description="Keep one kind of related entry.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Relation]:
    """What entries use (a chart's dataset, a dataset's connection) or what uses them.

    Use it before changing or deleting an entry, to see what depends on it. Auto-paginated.
    """
    return client.entries.relations_list(
        entry_ids,
        limit=config.http.cap(limit, all_=all),
        next=next,
        link_direction=link_direction,
        include_permissions_info=include_permissions_info,
        scope=scope,
    ).collect()


@mcp.tool(
    name="entries_permissions_get",
    annotations={**RO, "title": "Get DataLens permissions on entries"},
)
def permissions_get(
    entry_ids: EntryIDs, client: DataLensClient = Depends(datalens_client)
) -> EntriesPermissions:
    """What the caller may do with each entry, as a map by id.

    An entry that does not exist gives ``error: "NOT_FOUND"`` under its id.
    """
    return client.entries.permissions_get(entry_ids)


@mcp.tool(
    name="entries_revisions_list", annotations={**RO, "title": "List DataLens entry revisions"}
)
def revisions_list(
    entry_id: EntryID,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max revisions to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    rev_ids: Annotated[list[str] | None, Field(description="Keep only these revisions.")] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[Revision]:
    """The revisions of an entry: who saved it and when. Auto-paginated."""
    return client.entries.revisions_list(
        entry_id, limit=config.http.cap(limit, all_=all), next=next, rev_ids=rev_ids
    ).collect()


@mcp.tool(name="entries_rename", annotations={**WRITE_IDEMPOTENT, "title": "Rename DataLens entry"})
def rename(
    entry_id: EntryID,
    name: Annotated[str, Field(description="The new name.")],
    client: DataLensClient = Depends(datalens_client),
) -> ItemList[Renamed]:
    """Give an entry another name; its id and what refers to it stay."""
    return client.entries.rename(entry_id, name=name)
