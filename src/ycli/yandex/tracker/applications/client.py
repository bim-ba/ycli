"""Tracker external-applications client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.applications import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.applications.models import Application


class ApplicationsClient(Resource):
    """List the external applications issues can be linked to."""

    def list(self) -> ItemList[Application]:
        """``GET /applications`` → external applications that issues can be linked to.

        Returns:
            The external applications.

        Examples:
            >>> tracker.applications.list().root[0].id
            'my-application'
        """
        return self._session.send(endpoints.list_())
