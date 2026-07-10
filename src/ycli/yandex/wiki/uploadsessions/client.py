"""Declarative Yandex Wiki /upload_sessions client (uplink) — transport ONLY.

The binary upload pipeline: create a session, PUT the file bytes as one or more
``application/octet-stream`` parts, finish the session, then attach the file to a page
(see :meth:`AttachmentsClient.attach`). ``upload_part`` is the only binary method — its raw
bytes ride in an ``uplink.Body`` under a forced ``Content-Type: application/octet-stream``
(no ``@uplink.json``), with the 1-based part index as a query parameter.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter annotations
eagerly.
"""

import uplink

from ycli.yandex.wiki.base import WikiResource
from ycli.yandex.wiki.uploadsessions.models import (
    AbortActiveUploadsResult,
    UploadSession,
    UploadSessionCreate,
)


class UploadSessionsClient(WikiResource):
    """Declarative HTTP for ``/upload_sessions`` (create · get · upload-part · finish · abort)."""

    @uplink.returns.json()
    @uplink.json
    @uplink.post("upload_sessions")
    def _create(self, body: uplink.Body) -> UploadSession:  # ty: ignore[empty-body]
        """``POST /upload_sessions`` — open a session from a ready JSON body (see ``create``)."""

    def create(self, body: UploadSessionCreate) -> UploadSession:
        """Open an upload session from a typed ``UploadSessionCreate`` body. Returns the session.

        The returned ``session_id`` addresses the session for ``upload_part`` / ``finish``.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.create(
            ...     UploadSessionCreate(file_name="d.png", file_size=2048)
            ... ).session_id  # doctest: +SKIP
            '1e5c…'
        """
        return self._create(body=body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.get("upload_sessions/{session_id}")
    def get(self, session_id: uplink.Path) -> UploadSession:  # ty: ignore[empty-body]
        """``GET /upload_sessions/{session_id}`` → the session's current state (poll ``status``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.get("1e5c…").status  # doctest: +SKIP
            'in_progress'
        """

    @uplink.returns.json()
    @uplink.headers({"Content-Type": "application/octet-stream"})
    @uplink.put("upload_sessions/{session_id}/upload_part")
    def _upload_part(
        self,
        session_id: uplink.Path,
        part_number: uplink.Query,
        data: uplink.Body,
    ) -> UploadSession:  # ty: ignore[empty-body]
        """``PUT …/upload_part`` (octet-stream, raw bytes body; internal — see ``upload_part``)."""

    def upload_part(self, session_id: str, *, part_number: int, data: bytes) -> UploadSession:
        """Upload one file part as raw ``application/octet-stream`` bytes. Returns the session.

        ``part_number`` is 1-based (1 for the first part, +1 for each next). Parts may be
        5-16 MB except the last; a small file fits in a single ``part_number=1`` call.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.upload_part(
            ...     "1e5c…", part_number=1, data=b"\\x89PNG…"
            ... ).status  # doctest: +SKIP
            'in_progress'
        """
        return self._upload_part(session_id, part_number=part_number, data=data)

    @uplink.returns.json()
    @uplink.post("upload_sessions/{session_id}/finish")
    def finish(self, session_id: uplink.Path) -> UploadSession:  # ty: ignore[empty-body]
        """``POST /upload_sessions/{session_id}/finish`` — close the session so the file can attach.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.finish("1e5c…").status  # doctest: +SKIP
            'finished'
        """

    @uplink.returns.json()
    @uplink.post("upload_sessions/{session_id}/abort")
    def abort(self, session_id: uplink.Path) -> UploadSession:  # ty: ignore[empty-body]
        """``POST /upload_sessions/{session_id}/abort`` — cancel one in-progress session.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.abort("1e5c…").status  # doctest: +SKIP
            'aborted'
        """

    @uplink.returns.json()
    @uplink.post("upload_sessions/abort_active_uploads")
    def abort_all(self) -> AbortActiveUploadsResult:  # ty: ignore[empty-body]
        """``POST /upload_sessions/abort_active_uploads`` — cancel ALL active sessions (free quota).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.abort_all().status  # doctest: +SKIP
            'ok'
        """
