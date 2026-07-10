"""Declarative Yandex Wiki /pages/{id}/attachments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

from collections.abc import Sequence

import requests
import uplink

from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.attachments.models import (
    AttachedFileList,
    AttachmentCreate,
    AttachmentList,
    AttachmentsResponse,
    AttachResponse,
)
from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.uploadsessions.client import UploadSessionsClient
from ycli.yandex.wiki.uploadsessions.models import UploadSessionCreate


class AttachmentsClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/attachments`` (list + attach + binary download)."""

    @uplink.returns.json()
    @uplink.get("pages/{page_id}/attachments")
    def _list_page(
        self,
        page_id: uplink.Path,
        page_size: uplink.Query = 100,  # ty: ignore[invalid-parameter-default]
        cursor: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> AttachmentsResponse:  # ty: ignore[empty-body]
        """One raw page of attachments + ``next_cursor`` (internal; callers use ``list``)."""

    def list(self, page_id: int, *, limit: int | None = None) -> AttachmentList:
        """``GET /pages/{id}/attachments`` → flat :class:`AttachmentList`, draining ``next_cursor``.

        Capped at ``limit`` (``None`` = every attachment).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.list(12345, limit=50).root[0].name  # doctest: +SKIP
            'diagram.png'
        """
        strategy = CursorStrategy(
            extract=lambda page: page.results,
            next_of=lambda page: page.next_cursor,
        )
        attachments = strategy.collect(
            lambda cursor: self._list_page(page_id, page_size=100, cursor=cursor),
            limit,
        )
        return AttachmentList(attachments)

    @uplink.get("pages/{page_id}/attachments/{file_id}/download")
    def _download(self, page_id: uplink.Path, file_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """Raw binary response for a file by id (internal; callers use ``download``).

        No ``@uplink.returns.json()`` — this is a byte stream, not JSON."""

    def download(self, page_id: int, file_id: int) -> bytes:
        """``GET /pages/{id}/attachments/{file_id}/download`` → the file's raw bytes.

        Binary payload — SDK/CLI only (never MCP: base64 blobs are not an agent payload).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> Path("diagram.png").write_bytes(
            ...     client.attachments.download(12345, 678)
            ... )  # doctest: +SKIP
        """
        return self._download(page_id, file_id).content

    @uplink.get("pages/attachments/download_by_url")
    def _download_by_url(
        self,
        url: uplink.Query,
        download: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> requests.Response:  # ty: ignore[empty-body]
        """Raw binary response for a file by page-slug URL (internal; use ``download_by_url``)."""

    def download_by_url(self, url: str) -> bytes:
        """``GET /pages/attachments/download_by_url?url=`` → the file's raw bytes.

        Addresses a file by the ``<page-slug>/.files/<filename>`` URL instead of its numeric
        id; follows page redirects server-side. Binary payload — SDK/CLI only.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.download_by_url("data/x/.files/diagram.png")  # doctest: +SKIP
            b'\\x89PNG...'
        """
        return self._download_by_url(url=url, download="true").content

    @uplink.delete("pages/{page_id}/attachments/{file_id}")
    def _delete(self, page_id: uplink.Path, file_id: uplink.Path) -> requests.Response:  # ty: ignore[empty-body]
        """Raw ``204 No Content`` response for a delete (internal; callers use ``delete``).

        No ``@uplink.returns.json()`` — the API returns an empty ``204`` body; the transport's
        response hook has already raised on any non-2xx before this returns."""

    def delete(self, page_id: int, file_id: int) -> None:
        """``DELETE /pages/{id}/attachments/{file_id}`` — remove an attachment (``204``, no body).

        Returns ``None`` on success; raises a typed ``YandexError`` on any non-2xx.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.attachments.delete(12345, 678)  # doctest: +SKIP
        """
        self._delete(page_id, file_id)

    @uplink.returns.json()
    @uplink.json
    @uplink.post("pages/{page_id}/attachments")
    def _attach(self, page_id: uplink.Path, body: uplink.Body) -> AttachResponse:  # ty: ignore[empty-body]
        """``POST /pages/{id}/attachments`` — attach from a ready JSON body (see ``attach``)."""

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
        response = self._attach(
            page_id=page_id, body=body.model_dump(by_alias=True, exclude_none=True)
        )
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
