"""Tracker ``/gaps`` client on the httpx2 core: employee absences (admin-only)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.gaps import endpoints
from ycli.yandex.tracker.gaps.models import UserGapList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.tracker.gaps.models import GapCreated, GapsCreate


class GapsClient(Resource):
    """Create, search and delete employee absences (vacations, illness, trips, duty, …)."""

    def create(self, body: GapsCreate) -> GapCreated:
        """``POST /gaps`` → create up to 100 absences from a typed ``GapsCreate`` body.

        Needs Tracker administrator rights. Returns the absences actually saved.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.gaps.create(
            ...     GapsCreate(
            ...         gaps=[
            ...             GapInput(
            ...                 user="ann",
            ...                 workflow="trip",
            ...                 date_from="2026-07-10",
            ...                 date_to="2026-07-20",
            ...             )
            ...         ]
            ...     )
            ... ).gaps[0].id  # doctest: +SKIP
            '68340a1f2b4c1a3d5e7f9012'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True, mode="json")
        return self._session.send(endpoints.create_gaps(dumped))

    def search(
        self,
        users: Sequence[str],
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ) -> UserGapList:
        """``POST /gaps/_search`` (a read) → each user with the absences that overlap a window.

        ``users`` are up to 100 logins or ids; the window is ``date_from`` to ``date_to``
        (ISO 8601; the start defaults to now, the end must be after the start). Pages of
        users are joined; capped at ``limit`` users (``None`` = all). Needs administrator rights.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.gaps.search(["ann"], date_from="2026-07-01").root[0].gaps  # doctest: +SKIP
            []
        """
        window = {"from": date_from, "to": date_to}
        body = {"users": list(users), **{name: value for name, value in window.items() if value}}
        paged = endpoints.search_gaps(body)
        return UserGapList(list(self._session.iterate(paged, limit=limit)))

    def delete(self, gap_ids: Sequence[str]) -> None:
        """``DELETE /gaps?gapIds=…`` → delete absences by id (up to 100); unknown ids are ignored.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.gaps.delete(["68340a1f2b4c1a3d5e7f9011"])  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_gaps(gap_ids))
