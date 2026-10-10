"""DataLens licensing client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.licensing import endpoints

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.core.listing import Listing
    from ycli.yandex.datalens.licensing.models import (
        License,
        LicenseLimits,
        LicenseListed,
        LicenseSortField,
        LicenseStatus,
    )
    from ycli.yandex.models import ItemList, SortDirection


class LicensingClient(Resource):
    """Licences: the seats of the DataLens instance, who holds one, and how many there may be.

    A licence is a seat, and DataLens bills for seats (its pricing: the number of seats times
    the cost of one). The two writes here change that number and were never called: they are
    written from the document, not measured.
    """

    def licenses_list(
        self,
        *,
        user_ids: Sequence[str] | None = None,
        status: LicenseStatus | None = None,
        sort_by: LicenseSortField | None = None,
        order: SortDirection | None = None,
        limit: int | None = None,
        next: str | None = None,
    ) -> Listing[LicenseListed]:
        """``getLicenses`` → the licences of the instance, draining the pages.

        Capped at ``limit`` (``None`` = every licence).

        Args:
            user_ids: Only the licences of these users.
            status: Only the licences in this state: ``active``, ``expired`` or ``expiring``.
            sort_by: The field to sort by: ``createdAt`` or ``updatedAt``.
            order: ``asc`` or ``desc``.
            limit: The most licences to return; ``None`` returns every licence.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The licences: whose each is, its type, whether it is active and when its holder
            last signed in.

        Examples:
            >>> held = datalens.licensing.licenses_list(status="active").collect().items
            >>> [(licence.user_id, licence.license_type) for licence in held]
            [('user-1', 'creator')]
        """
        paged = endpoints.licenses_list(
            user_ids=user_ids, status=status, sort_by=sort_by, order=order
        )
        return self._session.iterate(paged, limit=limit, next=next)

    def licenses_assign(self, user_ids: Sequence[str]) -> ItemList[License]:
        """``assignLicenses`` — give each of these users a licence (not measured).

        A licence is a seat DataLens bills for. Written from the document: never called.

        Args:
            user_ids: The users to give a licence to.

        Returns:
            The licences given.

        Examples:
            >>> given = datalens.licensing.licenses_assign(["user-2"]).root
            >>> given[0].user_id
            'user-2'
        """
        return self._session.send(endpoints.licenses_assign(user_ids))

    def limit_get(self) -> LicenseLimits:
        """``getLicensesLimit`` → how many licences the instance may hold, now and next.

        Returns:
            ``current``: the limit in force, with the count of active licences; ``next``: the
            limit that takes over later, or ``None``.

        Examples:
            >>> limits = datalens.licensing.limit_get()
            >>> limits.current.value, limits.current.active_licenses_count
            (1, 1)
        """
        return self._session.send(endpoints.limit_get())

    def limit_set(self, value: int) -> LicenseLimits:
        """``setLicenseLimit`` — set how many licences the instance may hold (not measured).

        The limit is the number of seats DataLens bills for. Written from the document: never
        called.

        Args:
            value: The most licences the instance may hold.

        Returns:
            The limits after the change.

        Examples:
            >>> datalens.licensing.limit_set(3).current.value
            3
        """
        return self._session.send(endpoints.limit_set(value))
