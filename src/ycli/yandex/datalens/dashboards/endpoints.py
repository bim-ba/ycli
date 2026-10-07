"""DataLens dashboard operations, declared once (sans-IO).

Examples:
    >>> delete("d1", lock_token=None).body
    {'dashboardId': 'd1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.dashboards.models import (
    Dashboard,
    DashboardCreate,
    DashboardCreated,
    DashboardSaved,
    DashboardUpdate,
)
from ycli.yandex.datalens.models import RevisionBranch, one_revision
from ycli.yandex.datalens.schemas.dashboard import (
    CreateDashboardV2Args,
    DeleteDashboardArgs,
    GetDashboardV2Args,
    UpdateDashboardV2Args,
)
from ycli.yandex.datalens.schemas.shared import EntryBranch, EntryUpdateMode


def get(
    dashboard_id: str,
    *,
    rev_id: str | None,
    include_permissions: bool | None,
    include_links: bool | None,
    include_favorite: bool | None,
    branch: RevisionBranch | None,
    workbook_id: str | None,
) -> Endpoint[Dashboard]:
    one_revision(branch=branch, rev_id=rev_id)
    body = GetDashboardV2Args(
        dashboardId=dashboard_id,
        revId=rev_id,
        includePermissions=include_permissions,
        includeLinks=include_links,
        includeFavorite=include_favorite,
        branch=None if branch is None else EntryBranch(branch),
        workbookId=workbook_id,
    )
    return RPC("getDashboard", Dashboard, json=body, effect=Effect.READ)


def create(entry: DashboardCreate) -> Endpoint[DashboardCreated]:
    body = CreateDashboardV2Args(entry=entry)
    return RPC("createDashboard", DashboardCreated, json=body, effect=Effect.WRITE)


def update(
    entry: DashboardUpdate, *, mode: str, lock_token: str | None
) -> Endpoint[DashboardSaved]:
    body = UpdateDashboardV2Args(entry=entry, mode=EntryUpdateMode(mode), lockToken=lock_token)
    return RPC("updateDashboard", DashboardSaved, json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(dashboard_id: str, *, lock_token: str | None) -> Endpoint[None]:
    # Measured: 200 with `{}`; nothing in it to read.
    body = DeleteDashboardArgs(dashboardId=dashboard_id, lockToken=lock_token)
    return RPC("deleteDashboard", json=body, effect=Effect.DESTRUCTIVE)
