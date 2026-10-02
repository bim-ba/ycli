"""Tracker issue ``/attachments`` client on the httpx2 core: a JSON list plus two binary downloads.

Every method sends one declaration from :mod:`ycli.yandex.tracker.attachments.endpoints`. The
downloads return raw ``bytes``, which a JSON MCP result cannot carry, so they stay CLI/SDK-only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.attachments import endpoints

if TYPE_CHECKING:
    from ycli.yandex.tracker.attachments.models import AttachmentList


class AttachmentsClient(Resource):
    """Issue ``/attachments`` — a JSON list plus two binary downloads."""

    def list(self, issue_key: str) -> AttachmentList:
        """``GET /issues/{issue_key}/attachments`` → files attached to the issue (and its comments).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.list("JUNE-2").root[0].name  # doctest: +SKIP
            'picture.jpg'
        """
        return self._session.send(endpoints.list_attachments(issue_key))

    def download(self, issue_key: str, file_id: str, filename: str) -> bytes:
        """Download an attachment's raw bytes (a non-2xx answer raises a typed error).

        Binary output is CLI/SDK-only — never an MCP payload. In the CLI this feeds
        a ``BinaryResult`` (a file or stdout); the SDK returns the ``bytes``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.download("JUNE-2", "4159", "attachment.txt")[
            ...     :4
            ... ]  # doctest: +SKIP
            b'%PDF'
        """
        return self._session.send(endpoints.download_attachment(issue_key, file_id, filename))

    def download_thumbnail(self, issue_key: str, file_id: str) -> bytes:
        """Download a graphic attachment's preview-thumbnail bytes (a non-2xx answer raises).

        Only graphic files have a thumbnail; CLI/SDK-only, like :meth:`download`.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.download_thumbnail("JUNE-2", "4159")[:4]  # doctest: +SKIP
            b'\\x89PNG'
        """
        return self._session.send(endpoints.download_thumbnail(issue_key, file_id))
