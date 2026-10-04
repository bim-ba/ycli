"""Wiki ``/upload_sessions`` client on the httpx2 core — the binary upload pipeline.

Create a session, PUT the file bytes as one or more ``application/octet-stream`` parts, finish
the session, then attach the file to a page (see :meth:`AttachmentsClient.attach`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.uploadsessions import endpoints

if TYPE_CHECKING:
    from ycli.yandex.wiki.uploadsessions.models import (
        AbortActiveUploadsResult,
        UploadSession,
        UploadSessionCreate,
    )


class UploadSessionsClient(Resource):
    """``/upload_sessions``: create · get · upload-part · finish · abort."""

    def create(self, body: UploadSessionCreate) -> UploadSession:
        """Open an upload session from a typed ``UploadSessionCreate`` body. Returns the session.

        The returned ``session_id`` addresses the session for ``upload_part`` / ``finish``.

        Args:
            body: The file's name and size.

        Returns:
            The opened session.

        Examples:
            >>> from ycli.yandex.wiki.uploadsessions.models import UploadSessionCreate
            >>> body = UploadSessionCreate(file_name="report.xlsx", file_size=7340032)
            >>> wiki.uploadsessions.create(body).status
            'not_started'
        """
        return self._session.send(endpoints.create(body))

    def get(self, session_id: str) -> UploadSession:
        """``GET /upload_sessions/{session_id}`` → the session's current state (poll ``status``).

        Args:
            session_id: The session's id.

        Returns:
            The session.

        Examples:
            >>> session_id = "9c8b7a6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d"
            >>> wiki.uploadsessions.get(session_id).status
            'in_progress'
        """
        return self._session.send(endpoints.get(session_id))

    def upload_part(self, session_id: str, *, part_number: int, data: bytes) -> UploadSession:
        """Upload one file part as raw ``application/octet-stream`` bytes. Returns the session.

        ``part_number`` is 1-based (1 for the first part, +1 for each next). Parts may be
        5-16 MB except the last; a small file fits in a single ``part_number=1`` call.

        Args:
            session_id: The session's id.
            part_number: The part's 1-based number.
            data: The part's bytes.

        Returns:
            The session.

        Examples:
            >>> session_id = "9c8b7a6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d"
            >>> wiki.uploadsessions.upload_part(session_id, part_number=1, data=b"part").status
            'in_progress'
        """
        endpoint = endpoints.upload_part(session_id, part_number=part_number, data=data)
        return self._session.send(endpoint)

    def finish(self, session_id: str) -> UploadSession:
        """``POST /upload_sessions/{session_id}/finish`` — close the session so the file can attach.

        Args:
            session_id: The session's id.

        Returns:
            The finished session.

        Examples:
            >>> session_id = "9c8b7a6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d"
            >>> wiki.uploadsessions.finish(session_id).status
            'finished'
        """
        return self._session.send(endpoints.finish(session_id))

    def abort(self, session_id: str) -> UploadSession:
        """``POST /upload_sessions/{session_id}/abort`` — cancel one in-progress session.

        Args:
            session_id: The session's id.

        Returns:
            The aborted session.

        Examples:
            >>> session_id = "9c8b7a6d-5e4f-4a3b-8c2d-1e0f9a8b7c6d"
            >>> wiki.uploadsessions.abort(session_id).status
            'aborted'
        """
        return self._session.send(endpoints.abort(session_id))

    def abort_all(self) -> AbortActiveUploadsResult:
        """``POST /upload_sessions/abort_active_uploads`` — cancel ALL active sessions (free quota).

        Returns:
            The result of the abort.

        Examples:
            >>> wiki.uploadsessions.abort_all().status
            'ok'
        """
        return self._session.send(endpoints.abort_all())
