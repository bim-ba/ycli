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

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.create(
            ...     UploadSessionCreate(file_name="d.png", file_size=2048)
            ... ).session_id  # doctest: +SKIP
            '1e5c…'
        """
        payload = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_session(payload))

    def get(self, session_id: str) -> UploadSession:
        """``GET /upload_sessions/{session_id}`` → the session's current state (poll ``status``).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.get("1e5c…").status  # doctest: +SKIP
            'in_progress'
        """
        return self._session.send(endpoints.get_session(session_id))

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
        endpoint = endpoints.upload_part(session_id, part_number=part_number, data=data)
        return self._session.send(endpoint)

    def finish(self, session_id: str) -> UploadSession:
        """``POST /upload_sessions/{session_id}/finish`` — close the session so the file can attach.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.finish("1e5c…").status  # doctest: +SKIP
            'finished'
        """
        return self._session.send(endpoints.finish_session(session_id))

    def abort(self, session_id: str) -> UploadSession:
        """``POST /upload_sessions/{session_id}/abort`` — cancel one in-progress session.

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.abort("1e5c…").status  # doctest: +SKIP
            'aborted'
        """
        return self._session.send(endpoints.abort_session(session_id))

    def abort_all(self) -> AbortActiveUploadsResult:
        """``POST /upload_sessions/abort_active_uploads`` — cancel ALL active sessions (free quota).

        Example:
            >>> client = WikiClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.uploadsessions.abort_all().status  # doctest: +SKIP
            'ok'
        """
        return self._session.send(endpoints.abort_all_sessions())
