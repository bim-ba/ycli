"""DataLens dashboards FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dashboards.models import (
    Dashboard,
    DashboardCreate,
    DashboardCreated,
    DashboardSaved,
    DashboardUpdate,
)
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    OverBudget,
    PermissionsInfo,
    datalens_client,
)
from ycli.yandex.datalens.models import RevisionBranch, SaveMode
from ycli.yandex.models import Ack

mcp = FastMCP("datalens-dashboards")

DashboardID = Annotated[str, Field(description="Dashboard id.")]
LockToken = Annotated[
    str | None,
    Field(description="The token of the lock held on the dashboard, when it is locked."),
]
MODELS = "ycli.yandex.datalens.dashboards.models"


@mcp.tool(name="dashboards_get", annotations={**RO, "title": "Get DataLens dashboard"})
def get(
    dashboard_id: DashboardID,
    rev_id: Annotated[
        str | None,
        Field(description="The revision of the dashboard to read; the current when left out."),
    ] = None,
    include_permissions: PermissionsInfo = None,
    include_links: Annotated[
        bool | None, Field(description="Also say what the dashboard is linked to.")
    ] = None,
    include_favorite: Annotated[
        bool | None, Field(description="Also say whether the dashboard is a favourite.")
    ] = None,
    branch: Annotated[
        RevisionBranch | None, Field(description="Which version of it to read.")
    ] = None,
    workbook_id: Annotated[
        str | None, Field(description="The workbook the dashboard lies in.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Dashboard:
    """One dashboard: its tabs and the charts, selectors and texts on them.

    A real dashboard is large, 100 KB and more, which may be over what a client shows of a
    tool's reply: read a big one as a file (`ycli datalens dashboards get <id> > dash.json`).
    ``entry.data`` is what ``dashboards_update`` takes back.
    """
    return client.dashboards.get(
        dashboard_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
        workbook_id=workbook_id,
    )


@mcp.tool(name="dashboards_create", annotations={**WRITE, "title": "Create DataLens dashboard"})
def create(
    entry: Annotated[
        DashboardCreate,
        OverBudget(
            f"{MODELS}:DashboardCreate",
            "The new dashboard: where it lies (`workbookId`, `name`), `data` and `meta`.",
        ),
    ],
    client: DataLensClient = Depends(datalens_client),
) -> DashboardCreated:
    """Create a dashboard and return it with its id.

    ``data`` needs ``counter``, ``salt``, ``settings`` and ``tabs``; a tab may be empty.
    ``entry.meta`` must be an object, ``{}`` when empty: without it DataLens answers 400.
    """
    return client.dashboards.create(entry)


@mcp.tool(
    name="dashboards_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens dashboard"},
)
def update(
    entry: Annotated[
        DashboardUpdate,
        OverBudget(
            f"{MODELS}:DashboardUpdate",
            "The dashboard to save: its `entryId`, `data`, `meta` and `revId`.",
        ),
    ],
    mode: Annotated[
        SaveMode,
        Field(description="`save` keeps the dashboard as a draft; `publish` shows it to all."),
    ],
    lock_token: LockToken = None,
    client: DataLensClient = Depends(datalens_client),
) -> DashboardSaved:
    """Save a dashboard as given: read it, change ``data``, send it back whole."""
    return client.dashboards.update(entry, mode=mode, lock_token=lock_token)


@mcp.tool(
    name="dashboards_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens dashboard"}
)
def delete(
    dashboard_id: DashboardID,
    lock_token: LockToken = None,
    client: DataLensClient = Depends(datalens_client),
) -> Ack:
    """Delete a dashboard."""
    client.dashboards.delete(dashboard_id, lock_token=lock_token)
    return Ack.deleted("dashboard", dashboard_id)
