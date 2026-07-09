"""Declarative Yandex Wiki /pages/{id}/attachments client (uplink) — transport ONLY.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter
annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.pagination import CursorStrategy
from ycli.yandex.wiki.attachments.models import AttachmentList, AttachmentsResponse
from ycli.yandex.wiki.base import WikiResource


class AttachmentsClient(WikiResource):
    """Declarative HTTP for ``/pages/{id}/attachments`` (list + binary download)."""

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
