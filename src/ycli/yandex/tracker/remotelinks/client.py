"""Tracker issue ``/remotelinks`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.remotelinks import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkCreate


class RemoteLinksClient(Resource):
    """List, create and delete an issue's links to objects in external applications."""

    def list(self, issue_key: str) -> ItemList[RemoteLink]:
        """``GET /issues/{issue_key}/remotelinks`` → the issue's external-app links.

        Args:
            issue_key: The issue's key.

        Returns:
            The issue's external-app links.

        Examples:
            >>> tracker.remotelinks.list("JUNE-2").root[0].object_key
            'TEST-17'
        """
        return self._session.send(endpoints.list_(issue_key))

    def create(
        self, issue_key: str, body: RemoteLinkCreate, backlink: bool | None = None
    ) -> RemoteLink:
        """``POST /issues/{issue_key}/remotelinks?backlink=…`` — add an external link.

        ``backlink=True`` asks Tracker to also create the mirror link in the external app.

        Args:
            issue_key: The issue's key.
            body: The link's ``relationship``, external object ``key`` and ``origin``.
            backlink: ``True`` also creates the mirror link in the external app.

        Returns:
            The created external link.

        Examples:
            >>> from ycli.yandex.tracker.remotelinks.models import RemoteLinkCreate
            >>> tracker.remotelinks.create(
            ...     "JUNE-3",
            ...     RemoteLinkCreate.model_validate(
            ...         {
            ...             "relationship": "RELATES",
            ...             "key": "TEST-18",
            ...             "origin": "ru.yandex.bitbucket",
            ...         }
            ...     ),
            ...     backlink=True,
            ... ).object_key
            'TEST-18'
        """
        return self._session.send(endpoints.create(issue_key, body, backlink))

    def delete(self, issue_key: str, link_id: str) -> None:
        """Delete an external link (``DELETE …/remotelinks/{link_id}`` → 204). Raises on non-2xx.

        Args:
            issue_key: The issue's key.
            link_id: The external link's id.

        Examples:
            >>> tracker.remotelinks.delete("JUNE-6", "55")
        """
        self._session.send(endpoints.delete(issue_key, link_id))
