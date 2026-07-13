"""Declarative Tracker changelog client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.changelog.models import ChangelogList


class ChangelogClient(TrackerResource):
    """Declarative HTTP for ``/issues/{key}/changelog``."""

    @uplink.returns.json()
    @uplink.get("issues/{key}/changelog")
    def _page(
        self,
        key: uplink.Path,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
        change_id: uplink.Query("id") = None,  # ty: ignore[invalid-type-form]
    ) -> ChangelogList:  # ty: ignore[empty-body]
        """One raw ``/issues/{key}/changelog`` page (a bare JSON array); callers use ``list``."""

    def list(self, key: str, *, limit: int | None = None) -> ChangelogList:
        """All changelog events on an issue, draining the ``id=<last change id>`` cursor.

        ``GET /issues/{key}/changelog`` returns one page at a time (50 changes by default);
        each next page repeats with ``id=<id of the last change seen>`` until a page comes
        back empty. Capped at ``limit`` (``None`` = the full history).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.changelog.list(key="DATAENGINEERING-1").root[0].updated_by  # doctest: +SKIP
            'Сава Знатнов'
        """
        entries = self._drain_relative(
            extract=lambda page: page.root,
            id_of=lambda entry: entry.id,
            fetch_page=lambda cursor, per_page: self._page(
                key, per_page=per_page, change_id=cursor
            ),
            limit=limit,
        )
        return ChangelogList(entries)
