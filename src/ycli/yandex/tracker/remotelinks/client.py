"""Declarative Tracker issue remote-links client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkList


class RemoteLinksClient(TrackerResource):
    """Declarative HTTP for ``/issues/{issue_key}/remotelinks``."""

    @uplink.returns.json()
    @uplink.get("issues/{issue_key}/remotelinks")
    def list(self, issue_key: uplink.Path) -> RemoteLinkList:  # ty: ignore[empty-body]
        """``GET /issues/{issue_key}/remotelinks`` → the issue's external-app links.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.remotelinks.list("JUNE-2").root[0].object_key  # doctest: +SKIP
            'TEST-17'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("issues/{issue_key}/remotelinks")
    def create(
        self,
        issue_key: uplink.Path,
        body: uplink.Body,
        backlink: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> RemoteLink:  # ty: ignore[empty-body]
        """``POST /issues/{issue_key}/remotelinks?backlink=…`` — add an external link.

        ``backlink="true"`` asks Tracker to also create the mirror link in the external app.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.remotelinks.create(
            ...     "JUNE-2",
            ...     {"relationship": "RELATES", "key": "TEST-17", "origin": "ru.yandex.bitbucket"},
            ...     backlink="true",
            ... ).object_key  # doctest: +SKIP
            'TEST-17'
        """

    @uplink.delete("issues/{issue_key}/remotelinks/{link_id}")
    def _delete(self, issue_key: uplink.Path, link_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /issues/{issue_key}/remotelinks/{link_id}`` (204, no body; internal)."""

    def delete(self, issue_key: str, link_id: str) -> None:
        """Delete an external link (``DELETE …/remotelinks/{link_id}`` → 204). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.remotelinks.delete("JUNE-2", "51")  # doctest: +SKIP
        """
        self._delete(issue_key, link_id)
