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
    def list(
        self,
        key: uplink.Path,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
    ) -> ChangelogList:  # ty: ignore[empty-body]
        """``GET /issues/{key}/changelog`` → changelog listing (``perPage`` paging).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.changelog.list(key="DATAENGINEERING-1", per_page=50).root[
            ...     0
            ... ].updated_by  # doctest: +SKIP
            'Сава Знатнов'
        """
