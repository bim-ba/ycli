"""Tracker link-types client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.linktypes import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.models import LinkType


class LinkTypesClient(Resource):
    """List the kinds of links between issues."""

    def list(self) -> ItemList[LinkType]:
        """``GET /linktypes`` → link-type listing.

        Returns:
            The link types.

        Examples:
            >>> tracker.linktypes.list().root[0].id
            'relates'
        """
        return self._session.send(endpoints.list_())
