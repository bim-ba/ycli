"""Wiki ``/pages/{id}/attachments`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.wiki.attachments import endpoints
from ycli.yandex.wiki.attachments.models import AttachedFile, Attachment, AttachmentCreate
from ycli.yandex.wiki.uploadsessions.models import UploadSessionCreate

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.wiki.uploadsessions.client import UploadSessionsClient


class AttachmentsClient(Resource):
    """``/pages/{id}/attachments``: list, get, attach, upload, delete, download and preview.

    ``get`` and ``preview`` call operations Yandex does not document (they are in the live OpenAPI
    only), so their contract may change without notice.
    """

    def list(
        self,
        page_id: int,
        *,
        limit: int | None = None,
        order_by: str | None = None,
        order_direction: str | None = None,
    ) -> ItemList[Attachment]:
        """``GET /pages/{id}/attachments`` → ``ItemList[Attachment]``, draining ``next_cursor``.

        Capped at ``limit`` (``None`` = every attachment).

        Args:
            page_id: The page's id.
            limit: The most attachments to return; ``None`` returns every attachment.
            order_by: The sort field: ``name``, ``size`` or ``created_at``.
            order_direction: The sort direction for ``order_by``: ``asc`` or ``desc``.

        Returns:
            The page's attachments.

        Examples:
            >>> [file.name for file in wiki.attachments.list(5601, limit=20).root]
            ['spec.pdf', 'logo.png']
        """
        paged = endpoints.list_attachments(
            page_id, order_by=order_by, order_direction=order_direction
        )
        return ItemList[Attachment](list(self._session.iterate(paged, limit=limit)))

    def get(self, page_id: int, file_id: int) -> AttachedFile:
        """``GET /pages/{id}/attachments/{file_id}`` → one attachment's metadata.

        Undocumented by Yandex (live OpenAPI only), may change. The same descriptor ``attach``
        returns: name, size, MIME type, download URL, preview flag and virus-check status.

        Args:
            page_id: The page's id.
            file_id: The attachment's id.

        Returns:
            The attachment's metadata.

        Examples:
            >>> wiki.attachments.get(5607, 5621).mimetype
            'image/png'
        """
        return self._session.send(endpoints.get_attachment(page_id, file_id))

    def preview(self, page_id: int, file_id: int) -> bytes:
        r"""``GET /pages/{id}/attachments/{file_id}/preview`` → the preview image's raw bytes.

        Undocumented by Yandex (live OpenAPI only), may change. The bytes are returned as sent.
        For a file with no preview (``has_preview`` is false: not an image, say) the API sends
        ``200 image/png`` with the *base64 text* of a 1-pixel PNG instead of the PNG itself.
        Binary payload — SDK/CLI only.

        Args:
            page_id: The page's id.
            file_id: The attachment's id.

        Returns:
            The preview image's bytes.

        Examples:
            >>> wiki.attachments.preview(5608, 5622)
            b'\x89PNG preview bytes'
        """
        return self._session.send(endpoints.preview_attachment(page_id, file_id))

    def download(self, page_id: int, file_id: int) -> bytes:
        """``GET /pages/{id}/attachments/{file_id}/download`` → the file's raw bytes.

        Binary payload — SDK/CLI only (never MCP: base64 blobs are not an agent payload).

        Args:
            page_id: The page's id.
            file_id: The attachment's id.

        Returns:
            The file's bytes.

        Examples:
            >>> wiki.attachments.download(5603, 5613)
            b'%PDF-1.7 spec'
        """
        return self._session.send(endpoints.download_attachment(page_id, file_id))

    def download_by_url(self, url: str) -> bytes:
        """``GET /pages/attachments/download_by_url?url=`` → the file's raw bytes.

        Addresses a file by the ``<page-slug>/.files/<filename>`` URL instead of its numeric
        id; follows page redirects server-side. Binary payload — SDK/CLI only.

        Args:
            url: The file's ``<page-slug>/.files/<filename>`` URL.

        Returns:
            The file's bytes.

        Examples:
            >>> wiki.attachments.download_by_url("eng/specs/.files/spec.pdf")
            b'%PDF-1.7 by url'
        """
        return self._session.send(endpoints.download_by_url(url))

    def delete(self, page_id: int, file_id: int) -> None:
        """``DELETE /pages/{id}/attachments/{file_id}`` — remove an attachment (``204``, no body).

        Returns ``None`` on success; raises a typed ``YandexError`` on any non-2xx.

        Args:
            page_id: The page's id.
            file_id: The attachment's id.

        Examples:
            >>> wiki.attachments.delete(5604, 5614)
        """
        self._session.send(endpoints.delete_attachment(page_id, file_id))

    def attach(self, page_id: int, session_ids: Sequence[str]) -> ItemList[AttachedFile]:
        """``POST /pages/{id}/attachments`` — attach file(s) from finished upload sessions.

        ``session_ids`` are the ``session_id`` of each finished upload session (see
        :class:`UploadSessionsClient`). Returns the flat list of newly-attached files.

        Args:
            page_id: The page's id.
            session_ids: The ids of the finished upload sessions to attach.

        Returns:
            The newly-attached files.

        Examples:
            >>> wiki.attachments.attach(5605, ["s-5605-a", "s-5605-b"]).root[1].name
            'b.png'
        """
        body = AttachmentCreate(upload_sessions=list(session_ids))
        payload = body.model_dump(by_alias=True, exclude_none=True)
        response = self._session.send(endpoints.attach_files(page_id, payload))
        return ItemList[AttachedFile](response.results)

    def upload(
        self,
        sessions: UploadSessionsClient,
        page_id: int,
        *,
        file_name: str,
        data: bytes,
    ) -> ItemList[AttachedFile]:
        """Run the whole upload pipeline for one file, then attach it to ``page_id``.

        Drives the four steps end to end against the injected ``sessions`` client: open a
        session sized to ``data``, PUT the bytes as a single octet-stream part, finish the
        session, then ``attach`` the finished session to the page. Small-file path — the bytes
        go up as one ``part_number=1`` part (chunk large files with ``upload_part`` directly).
        Returns the flat list of newly-attached files.

        Args:
            sessions: The upload-sessions client that opens, fills and finishes the session.
            page_id: The page's id.
            file_name: The name the attachment gets.
            data: The file's bytes.

        Returns:
            The newly-attached files.

        Examples:
            >>> wiki.attachments.upload(
            ...     wiki.uploadsessions, 5606, file_name="diagram.txt", data=b"hello"
            ... ).root[0].name
            'diagram.txt'
        """
        session = sessions.create(UploadSessionCreate(file_name=file_name, file_size=len(data)))
        session_id = session.session_id or ""
        sessions.upload_part(session_id, part_number=1, data=data)
        sessions.finish(session_id=session_id)
        return self.attach(page_id, [session_id])
