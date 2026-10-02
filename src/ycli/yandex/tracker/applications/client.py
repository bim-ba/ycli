"""Tracker external-applications client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.applications import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.applications.models import ApplicationList


class ApplicationsClient(Resource):
    """List the external applications issues can be linked to."""

    def list(self) -> ApplicationList:
        """``GET /applications`` → external applications that issues can be linked to.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.applications.list().root[0].id  # doctest: +SKIP
            'my-application'
        """
        return self._session.send(endpoints.list_applications())
