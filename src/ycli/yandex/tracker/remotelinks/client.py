"""Tracker issue ``/remotelinks`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.remotelinks import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkList


class RemoteLinksClient(Resource):
    """List, create and delete an issue's links to objects in external applications."""

    def list(self, issue_key: str) -> RemoteLinkList:
        """``GET /issues/{issue_key}/remotelinks`` → the issue's external-app links.

        Args:
            issue_key: The issue's key.

        Returns:
            The issue's external-app links.

        Examples:
            >>> tracker.remotelinks.list("JUNE-2").root[0].object_key
            'TEST-17'
        """
        return self._session.send(endpoints.list_remote_links(issue_key))

    def create(
        self, issue_key: str, body: dict[str, Any], backlink: str | None = None
    ) -> RemoteLink:
        """``POST /issues/{issue_key}/remotelinks?backlink=…`` — add an external link.

        ``backlink="true"`` asks Tracker to also create the mirror link in the external app.

        Args:
            issue_key: The issue's key.
            body: The link's ``relationship``, external object ``key`` and ``origin``.
            backlink: ``"true"`` also creates the mirror link in the external app.

        Returns:
            The created external link.

        Examples:
            >>> tracker.remotelinks.create(
            ...     "JUNE-3",
            ...     {"relationship": "BLOCKS", "key": "TEST-18", "origin": "ru.yandex.bitbucket"},
            ...     backlink="true",
            ... ).object_key
            'TEST-18'
        """
        return self._session.send(endpoints.create_remote_link(issue_key, body, backlink))

    def delete(self, issue_key: str, link_id: str) -> None:
        """Delete an external link (``DELETE …/remotelinks/{link_id}`` → 204). Raises on non-2xx.

        Args:
            issue_key: The issue's key.
            link_id: The external link's id.

        Examples:
            >>> tracker.remotelinks.delete("JUNE-6", "55")
        """
        self._session.send(endpoints.delete_remote_link(issue_key, link_id))
