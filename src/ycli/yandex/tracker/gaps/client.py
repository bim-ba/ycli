"""Tracker ``/gaps`` client on the httpx2 core: employee absences (admin-only)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.gaps import endpoints
from ycli.yandex.tracker.gaps.models import GapsSearch, UserGaps

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.tracker.gaps.models import GapCreated, GapsCreate


class GapsClient(Resource):
    """Create, search and delete employee absences (vacations, illness, trips, duty, …)."""

    def create(self, body: GapsCreate) -> GapCreated:
        """``POST /gaps`` → create up to 100 absences from a typed ``GapsCreate`` body.

        Needs Tracker administrator rights. Returns the absences actually saved.

        Args:
            body: The absences to create.

        Returns:
            The absences actually saved.

        Examples:
            >>> from ycli.yandex.tracker.gaps.models import GapInput, GapsCreate, GapWorkflow
            >>> gap = GapInput(
            ...     user="ann",
            ...     workflow="vacation",
            ...     date_from="2026-07-01T00:00:00.000Z",
            ...     date_to="2026-07-15T00:00:00.000Z",
            ... )
            >>> tracker.gaps.create(GapsCreate(gaps=[gap])).gaps[0].id
            '68340a1f2b4c1a3d5e7f9011'
        """
        return self._session.send(endpoints.create(body))

    def search(
        self,
        users: Sequence[str],
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ) -> ItemList[UserGaps]:
        """``POST /gaps/_search`` (a read) → each user with the absences that overlap a window.

        ``users`` are up to 100 logins or ids; the window is ``date_from`` to ``date_to``
        (ISO 8601; the start defaults to now, the end must be after the start). Pages of
        users are joined; capped at ``limit`` users (``None`` = all). Needs administrator rights.

        Args:
            users: The logins or ids of the users to look up.
            date_from: Window start (ISO 8601); defaults to now.
            date_to: Window end (ISO 8601); must be after the start.
            limit: The most users to return; ``None`` returns all.

        Returns:
            Each user with the absences that overlap the window.

        Examples:
            >>> found = tracker.gaps.search(
            ...     ["ann", "bob"],
            ...     date_from="2026-07-01T00:00:00.000Z",
            ...     date_to="2026-08-31T23:59:59.999Z",
            ... )
            >>> [(user.user.login, len(user.gaps)) for user in found.root]
            [('ann', 1), ('bob', 0)]
        """
        body = GapsSearch(users=list(users), date_from=date_from or None, date_to=date_to or None)
        paged = endpoints.search(body)
        return ItemList[UserGaps](list(self._session.iterate(paged, limit=limit)))

    def delete(self, gap_ids: Sequence[str]) -> None:
        """``DELETE /gaps?gapIds=…`` → delete absences by id (up to 100); unknown ids are ignored.

        Args:
            gap_ids: The ids of the absences to delete.

        Examples:
            >>> tracker.gaps.delete(["68340a1f2b4c1a3d5e7f9011", "68340a1f2b4c1a3d5e7f9012"])
        """
        self._session.send(endpoints.delete(gap_ids))
