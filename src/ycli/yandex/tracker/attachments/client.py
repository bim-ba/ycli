"""Tracker issue ``/attachments`` client on the httpx2 core: reads, uploads, deletes, downloads.

Every method sends one declaration from :mod:`ycli.yandex.tracker.attachments.endpoints`. The
downloads return raw ``bytes``, which a JSON MCP result cannot carry, so they stay CLI/SDK-only;
the uploads take ``bytes`` and reach MCP as base64.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.attachments import endpoints

if TYPE_CHECKING:
    from ycli.yandex.models import ItemList
    from ycli.yandex.tracker.attachments.models import Attachment


class AttachmentsClient(Resource):
    """Issue ``/attachments`` — list, get, upload, delete, plus two binary downloads."""

    def list(self, issue_key: str) -> ItemList[Attachment]:
        """``GET /issues/{issue_key}/attachments`` → files attached to the issue (and its comments).

        Args:
            issue_key: The issue key.

        Returns:
            The issue's attachments.

        Examples:
            >>> tracker.attachments.list("JUNE-2").root[0].name
            'picture.jpg'
        """
        return self._session.send(endpoints.list_(issue_key))

    # violation(arch-1): CLI-only, bytes do not round-trip an MCP tool result
    def download(self, issue_key: str, file_id: str, filename: str) -> bytes:
        """Download an attachment's raw bytes (a non-2xx answer raises a typed error).

        Binary output is CLI/SDK-only — never an MCP payload. In the CLI this feeds
        a ``BinaryResult`` (a file or stdout); the SDK returns the ``bytes``.

        Args:
            issue_key: The issue key.
            file_id: The attachment's id.
            filename: The attachment's file name, as it is in the download path.

        Returns:
            The attachment's raw bytes.

        Examples:
            >>> tracker.attachments.download("JUNE-3", "4159", "report.pdf")[:4]
            b'%PDF'
        """
        return self._session.send(endpoints.download(issue_key, file_id, filename))

    # violation(arch-1): CLI-only, bytes do not round-trip an MCP tool result
    def thumbnails_download(self, issue_key: str, file_id: str) -> bytes:
        r"""Download a graphic attachment's preview-thumbnail bytes (a non-2xx answer raises).

        Only graphic files have a thumbnail; CLI/SDK-only, like :meth:`download`.

        Args:
            issue_key: The issue key.
            file_id: The attachment's id.

        Returns:
            The thumbnail's raw bytes.

        Examples:
            >>> tracker.attachments.thumbnails_download("JUNE-4", "4160")[:4]
            b'\x89PNG'
        """
        return self._session.send(endpoints.thumbnails_download(issue_key, file_id))

    def get(self, issue_key: str, file_id: str) -> Attachment:
        """``GET /issues/{issue_key}/attachments/{file_id}`` → the attachment's metadata.

        The raw bytes are :meth:`download`; this returns name, size, MIME type and uploader.

        Args:
            issue_key: The issue key.
            file_id: The attachment's id.

        Returns:
            The attachment's metadata.

        Examples:
            >>> tracker.attachments.get("JUNE-5", "4161").mimetype
            'text/plain'
        """
        return self._session.send(endpoints.get(issue_key, file_id))

    def delete(self, issue_key: str, file_id: str) -> None:
        """``DELETE /issues/{issue_key}/attachments/{file_id}`` → 204; raises on non-2xx.

        Args:
            issue_key: The issue key.
            file_id: The attachment's id.

        Examples:
            >>> tracker.attachments.delete("JUNE-6", "4162")
        """
        self._session.send(endpoints.delete(issue_key, file_id))

    def upload(
        self, issue_key: str, *, filename: str, data: bytes, rename_to: str | None = None
    ) -> Attachment:
        """``POST /issues/{issue_key}/attachments`` → attach a file (multipart field ``file``).

        ``filename`` names the part; ``rename_to`` (the ``?filename=`` query) stores the file
        under another name. Returns the created :class:`Attachment`.

        Args:
            issue_key: The issue key.
            filename: The multipart part's file name.
            data: The file's bytes.
            rename_to: The name to store the file under; ``None`` keeps ``filename``.

        Returns:
            The created attachment.

        Examples:
            >>> tracker.attachments.upload(
            ...     "JUNE-7", filename="upload.txt", data=b"attachment bytes", rename_to="kept.txt"
            ... ).id
            '4161'
        """
        endpoint = endpoints.upload(issue_key, filename=filename, data=data, rename_to=rename_to)
        return self._session.send(endpoint)

    def upload_temp(
        self, *, filename: str, data: bytes, rename_to: str | None = None
    ) -> Attachment:
        """``POST /attachments`` → upload a temporary file to attach later, once.

        The returned ``id`` goes into ``attachmentIds`` of an issue or comment body; Tracker
        accepts it for one attachment only.

        Args:
            filename: The multipart part's file name.
            data: The file's bytes.
            rename_to: The name to store the file under; ``None`` keeps ``filename``.

        Returns:
            The temporary attachment, whose ``id`` is the one to attach.

        Examples:
            >>> tracker.attachments.upload_temp(
            ...     filename="temp-upload.txt", data=b"temporary bytes", rename_to="scratch.txt"
            ... ).id
            '4170'
        """
        endpoint = endpoints.upload_temp(filename=filename, data=data, rename_to=rename_to)
        return self._session.send(endpoint)

    def import_(
        self,
        issue_key: str,
        *,
        filename: str,
        created_at: str,
        created_by: str,
        data: bytes,
    ) -> Attachment:
        """Import a file (multipart/form-data) preserving its ``createdAt`` / ``createdBy``.

        ``data`` are the raw file bytes; ``filename`` / ``created_at`` / ``created_by`` become
        query parameters. Returns the created ``Attachment``.

        Args:
            issue_key: The issue's key.
            filename: The attachment's file name.
            created_at: The source creation time.
            created_by: The source author.
            data: The raw file bytes.

        Returns:
            The created attachment.

        Examples:
            >>> tracker.attachments.import_(
            ...     "JUNE-5",
            ...     filename="renamed.png",
            ...     created_at="2022-05-06T07:08:09.000+0000",
            ...     created_by="16",
            ...     data=b"PNGDATA",
            ... ).name
            'renamed.png'
        """
        endpoint = endpoints.import_(
            issue_key,
            filename=filename,
            created_at=created_at,
            created_by=created_by,
            data=data,
        )
        return self._session.send(endpoint)

    # violation(arch-1): CLI-only, a comment's file is read from disk as raw bytes
    def import_for_comment(
        self,
        issue_key: str,
        comment_id: str,
        *,
        filename: str,
        created_at: str,
        created_by: str,
        data: bytes,
    ) -> Attachment:
        """Import a file onto a comment, preserving its ``createdAt`` / ``createdBy``.

        ``POST /issues/{issue_key}/comments/{comment_id}/attachments/_import`` (multipart);
        ``created_at`` must fall between the comment's creation and its last update (for a
        comment never edited, exactly its ``createdAt``), else Tracker answers 422. Returns the
        created ``Attachment``.

        Args:
            issue_key: The issue's key.
            comment_id: The comment's id.
            filename: The attachment's file name.
            created_at: The source creation time.
            created_by: The source author.
            data: The raw file bytes.

        Returns:
            The created attachment.

        Examples:
            >>> tracker.attachments.import_for_comment(
            ...     "JUNE-7",
            ...     "2238",
            ...     filename="scan.png",
            ...     created_at="2024-07-08T09:10:11.000+0000",
            ...     created_by="18",
            ...     data=b"PNGDATA",
            ... ).name
            'scan.png'
        """
        endpoint = endpoints.import_for_comment(
            issue_key,
            comment_id,
            filename=filename,
            created_at=created_at,
            created_by=created_by,
            data=data,
        )
        return self._session.send(endpoint)
