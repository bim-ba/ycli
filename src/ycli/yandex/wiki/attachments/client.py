"""Wiki ``/pages/{id}/attachments`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.attachments import endpoints
from ycli.yandex.wiki.attachments.models import AttachedFileList, AttachmentCreate, AttachmentList
from ycli.yandex.wiki.uploadsessions.models import UploadSessionCreate

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.wiki.uploadsessions.client import UploadSessionsClient


class AttachmentsClient(Resource):
    """``/pages/{id}/attachments``: list, attach, upload, delete and binary download."""

    def list(self, page_id: int, *, limit: int | None = None) -> AttachmentList:
        """``GET /pages/{id}/attachments`` → flat :class:`AttachmentList`, draining ``next_cursor``.

        Capped at ``limit`` (``None`` = every attachment).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.list(12345, limit=50).root[0].name  # doctest: +SKIP
            'diagram.png'
        """
        paged = endpoints.list_attachments(page_id)
        return AttachmentList(list(self._session.iterate(paged, limit=limit)))

    def download(self, page_id: int, file_id: int) -> bytes:
        """``GET /pages/{id}/attachments/{file_id}/download`` → the file's raw bytes.

        Binary payload — SDK/CLI only (never MCP: base64 blobs are not an agent payload).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> Path("diagram.png").write_bytes(
            ...     client.attachments.download(12345, 678)
            ... )  # doctest: +SKIP
        """
        return self._session.send(endpoints.download_attachment(page_id, file_id))

    def download_by_url(self, url: str) -> bytes:
        """``GET /pages/attachments/download_by_url?url=`` → the file's raw bytes.

        Addresses a file by the ``<page-slug>/.files/<filename>`` URL instead of its numeric
        id; follows page redirects server-side. Binary payload — SDK/CLI only.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.download_by_url("data/x/.files/diagram.png")  # doctest: +SKIP
            b'\\x89PNG...'
        """
        return self._session.send(endpoints.download_by_url(url))

    def delete(self, page_id: int, file_id: int) -> None:
        """``DELETE /pages/{id}/attachments/{file_id}`` — remove an attachment (``204``, no body).

        Returns ``None`` on success; raises a typed ``YandexError`` on any non-2xx.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.delete(12345, 678)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_attachment(page_id, file_id))

    def attach(self, page_id: int, session_ids: Sequence[str]) -> AttachedFileList:
        """``POST /pages/{id}/attachments`` — attach file(s) from finished upload sessions.

        ``session_ids`` are the ``session_id`` of each finished upload session (see
        :class:`UploadSessionsClient`). Returns the flat list of newly-attached files.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.attach(12345, ["1e5c…"]).root[0].name  # doctest: +SKIP
            'diagram.png'
        """
        body = AttachmentCreate(upload_sessions=list(session_ids))
        payload = body.model_dump(by_alias=True, exclude_none=True)
        response = self._session.send(endpoints.attach_files(page_id, payload))
        return AttachedFileList(response.results)

    def upload(
        self,
        sessions: UploadSessionsClient,
        page_id: int,
        *,
        file_name: str,
        data: bytes,
    ) -> AttachedFileList:
        """Run the whole upload pipeline for one file, then attach it to ``page_id``.

        Drives the four steps end to end against the injected ``sessions`` client: open a
        session sized to ``data``, PUT the bytes as a single octet-stream part, finish the
        session, then ``attach`` the finished session to the page. Small-file path — the bytes
        go up as one ``part_number=1`` part (chunk large files with ``upload_part`` directly).
        Returns the flat list of newly-attached files.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.upload(
            ...     client.uploadsessions, 12345, file_name="d.png", data=b"\\x89PNG…"
            ... ).root[0].name  # doctest: +SKIP
            'd.png'
        """
        session = sessions.create(UploadSessionCreate(file_name=file_name, file_size=len(data)))
        session_id = session.session_id or ""
        sessions.upload_part(session_id, part_number=1, data=data)
        sessions.finish(session_id=session_id)
        return self.attach(page_id, [session_id])
