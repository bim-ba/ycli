"""DataLens dashboards client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.dashboards import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.dashboards.models import (
        Dashboard,
        DashboardCreate,
        DashboardCreated,
        DashboardSaved,
        DashboardUpdate,
    )


class DashboardsClient(Resource):
    """Dashboards: tabs of charts, selectors and texts."""

    def get(
        self,
        dashboard_id: str,
        *,
        rev_id: str | None = None,
        include_permissions: bool | None = None,
        include_links: bool | None = None,
        include_favorite: bool | None = None,
        branch: str | None = None,
        workbook_id: str | None = None,
    ) -> Dashboard:
        """``getDashboard`` → one dashboard: its tabs and what stands on them.

        A real dashboard is large: three of the owner's came as 81, 114 and 210 KB.

        Args:
            dashboard_id: The dashboard's id.
            rev_id: The revision to read; the current one when left out.
            include_permissions: Also say what the caller may do with it.
            include_links: Also say what it is linked to.
            include_favorite: Also say whether it is a favourite of the caller.
            branch: Which version to read: ``saved`` or ``published``.
            workbook_id: The workbook the dashboard lies in.

        Returns:
            The dashboard.

        Examples:
            >>> dashboard = datalens.dashboards.get("dash0000000001")
            >>> dashboard.entry.entry_id, [tab.title for tab in dashboard.entry.data.tabs]
            ('dash0000000001', ['Sales'])
        """
        return self._session.send(
            endpoints.get(
                dashboard_id,
                rev_id=rev_id,
                include_permissions=include_permissions,
                include_links=include_links,
                include_favorite=include_favorite,
                branch=branch,
                workbook_id=workbook_id,
            )
        )

    def create(self, entry: DashboardCreate) -> DashboardCreated:
        """``createDashboard`` — create a dashboard → it, with its id.

        ``entry`` says where it lies (``workbookId`` and ``name``) and what it holds: ``data``
        needs ``counter``, ``salt``, ``settings`` and ``tabs``, and a tab may be empty. The
        ``data`` of a dashboard read with ``get`` is a valid one.

        Args:
            entry: The new dashboard: where it lies, its tabs and its settings.

        Returns:
            The created dashboard.

        Examples:
            >>> from ycli.yandex.datalens.dashboards.models import DashboardCreate
            >>> tab = {"id": "t1", "title": "Sales", "items": [], "layout": []}
            >>> new = DashboardCreate.model_validate(
            ...     {
            ...         "workbookId": "wb000000000001",
            ...         "name": "Sales",
            ...         "data": {"counter": 1, "salt": "s", "settings": {}, "tabs": [tab]},
            ...     }
            ... )
            >>> datalens.dashboards.create(new).entry.entry_id
            'dash0000000001'
        """
        return self._session.send(endpoints.create(entry))

    def update(
        self, entry: DashboardUpdate, *, mode: str, lock_token: str | None = None
    ) -> DashboardSaved:
        """``updateDashboard`` — save a dashboard as given → what was saved.

        ``entry`` names the dashboard by its ``entryId`` and replaces what it holds: read it,
        change ``data``, send it back whole. ``save`` keeps a draft, ``publish`` makes it the
        version everyone sees.

        Args:
            entry: The dashboard to save: its ``entryId``, ``data``, ``meta`` and ``revId``.
            mode: ``save`` or ``publish``.
            lock_token: The token of the lock held on the dashboard, when it is locked.

        Returns:
            The dashboard as saved.

        Examples:
            >>> from ycli.yandex.datalens.dashboards.models import DashboardUpdate
            >>> tab = {"id": "t1", "title": "Sales", "items": [], "layout": []}
            >>> change = DashboardUpdate.model_validate(
            ...     {
            ...         "entryId": "dash0000000001",
            ...         "data": {"counter": 2, "salt": "s", "settings": {}, "tabs": [tab]},
            ...     }
            ... )
            >>> datalens.dashboards.update(change, mode="save").entry.rev_id
            'rev2'
        """
        return self._session.send(endpoints.update(entry, mode=mode, lock_token=lock_token))

    def delete(self, dashboard_id: str, *, lock_token: str | None = None) -> None:
        """``deleteDashboard`` — delete a dashboard.

        Args:
            dashboard_id: The dashboard's id.
            lock_token: The token of the lock held on the dashboard, when it is locked.

        Examples:
            >>> datalens.dashboards.delete("dash0000000001")
        """
        self._session.send(endpoints.delete(dashboard_id, lock_token=lock_token))
