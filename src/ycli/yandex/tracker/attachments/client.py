"""Declarative Tracker issue-attachments client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

The binary downloads deliberately skip ``@uplink.returns.json()`` and return the raw
``requests.Response``; the public wrappers expose ``resp.content`` (``bytes``). The transport
response hook raises a typed ``YandexError`` on any non-2xx, so a failed GET raises before a
caller ever touches ``.content``. ``import requests`` in a ``client.py`` is intentional here —
this is the canonical binary-download pattern the rest of the project copies.
"""

import requests
import uplink

from ycli.yandex.tracker.attachments.models import AttachmentList
from ycli.yandex.tracker.base import TrackerResource


class AttachmentsClient(TrackerResource):
    """Declarative HTTP for issue ``/attachments`` — a JSON list plus two binary downloads."""

    @uplink.returns.json()
    @uplink.get("issues/{issue_key}/attachments")
    def list(self, issue_key: uplink.Path) -> AttachmentList:  # ty: ignore[empty-body]
        """``GET /issues/{issue_key}/attachments`` → files attached to the issue (and its comments).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.list("JUNE-2").root[0].name  # doctest: +SKIP
            'picture.jpg'
        """

    @uplink.get("issues/{issue_key}/attachments/{file_id}/{filename}")
    def _download(
        self,
        issue_key: uplink.Path,
        file_id: uplink.Path,
        filename: uplink.Path,
    ) -> requests.Response:  # ty: ignore[empty-body]
        """GET the raw attachment bytes (internal; callers use :meth:`download`)."""

    def download(self, issue_key: str, file_id: str, filename: str) -> bytes:
        """Download an attachment's raw bytes (raises on non-2xx via the transport hook).

        Binary output is CLI/SDK-only — never an MCP payload. In the CLI this feeds
        ``ycli.cli.binary.write_output`` (a file or stdout); the SDK returns the ``bytes``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.download("JUNE-2", "4159", "attachment.txt")[
            ...     :4
            ... ]  # doctest: +SKIP
            b'%PDF'
        """
        return self._download(issue_key, file_id, filename).content

    @uplink.get("issues/{issue_key}/thumbnails/{file_id}")
    def _download_thumbnail(
        self,
        issue_key: uplink.Path,
        file_id: uplink.Path,
    ) -> requests.Response:  # ty: ignore[empty-body]
        """GET the raw preview-thumbnail bytes (internal; use :meth:`download_thumbnail`)."""

    def download_thumbnail(self, issue_key: str, file_id: str) -> bytes:
        """Download a graphic attachment's preview-thumbnail bytes (raises on non-2xx).

        Only graphic files have a thumbnail; CLI/SDK-only, like :meth:`download`.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.download_thumbnail("JUNE-2", "4159")[:4]  # doctest: +SKIP
            b'\\x89PNG'
        """
        return self._download_thumbnail(issue_key, file_id).content
