"""DataLens shared entries FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import LIMIT_CAP, RO, WRITE, app_config, datalens_client
from ycli.yandex.datalens.models import AccessBindingDelta, Operation, SubjectWithBindings
from ycli.yandex.models import ItemList

mcp = FastMCP("datalens-sharedentries")

SharedEntryID = Annotated[
    str, Field(description="Id of a shared entry: one that lies in a collection.")
]


@mcp.tool(
    name="sharedentries_access_bindings_list",
    annotations={**RO, "title": "List the roles on a DataLens shared entry"},
)
def access_bindings_list(
    entry_id: SharedEntryID,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max subjects to return; {LIMIT_CAP}")
    ] = None,
    get_inherited_bindings: Annotated[
        bool | None, Field(description="Also list the roles inherited from above.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[SubjectWithBindings]:
    """Who has which role on a shared entry, auto-paginated.

    An entry that lies in a workbook, or an id nothing knows, answers an empty list.
    """
    return client.sharedentries.access_bindings_list(
        entry_id,
        limit=config.http.cap(limit),
        get_inherited_bindings=get_inherited_bindings,
    )


@mcp.tool(
    name="sharedentries_access_bindings_update",
    annotations={**WRITE, "title": "Change the roles on a DataLens shared entry"},
)
def access_bindings_update(
    entry_id: SharedEntryID,
    deltas: Annotated[
        list[AccessBindingDelta], Field(description="The roles to add (`ADD`) and remove.")
    ],
    client: DataLensClient = Depends(datalens_client),
) -> Operation:
    """Give or take away roles on a shared entry; the roles not named stay as they are.

    The roles are ``datalens.sharedEntries.*`` (``viewer``, ``admin``, …).
    """
    return client.sharedentries.access_bindings_update(entry_id, deltas=deltas)
