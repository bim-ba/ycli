"""Tracker link-types client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.linktypes import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.linktypes.models import LinkTypeList


class LinkTypesClient(Resource):
    """List the kinds of links between issues."""

    def list(self) -> LinkTypeList:
        """``GET /linktypes`` → link-type listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.linktypes.list().root[0].id  # doctest: +SKIP
            'relates'
        """
        return self._session.send(endpoints.list_link_types())
