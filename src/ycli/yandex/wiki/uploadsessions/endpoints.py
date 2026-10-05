"""Wiki ``/upload_sessions`` — the binary upload pipeline, declared once (sans-IO).

Create a session, PUT the file bytes as one or more ``application/octet-stream`` parts, finish
the session, then attach the file to a page. Aborting is a ``POST`` that discards uploaded parts,
so both aborts declare themselves destructive.

Examples:
    >>> parts_upload("s-1", part_number=2, data=b"x").params
    {'part_number': 2}
    >>> abort("s-1").effect
    <Effect.DESTRUCTIVE: 'destructive'>
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Effect, Endpoint, segment
from ycli.yandex.wiki.uploadsessions.models import (
    AbortActiveUploadsResult,
    UploadSession,
    UploadSessionCreate,
)


def create(body: UploadSessionCreate) -> Endpoint[UploadSession]:
    return Endpoint(HTTPMethod.POST, "upload_sessions", UploadSession, json=body)


def get(session_id: str) -> Endpoint[UploadSession]:
    return Endpoint(HTTPMethod.GET, f"upload_sessions/{segment(session_id)}", UploadSession)


def parts_upload(session_id: str, *, part_number: int, data: bytes) -> Endpoint[UploadSession]:
    """``PUT …/upload_part``: the raw bytes as the body, the 1-based part index in the query."""
    return Endpoint(
        HTTPMethod.PUT,
        f"upload_sessions/{segment(session_id)}/upload_part",
        UploadSession,
        params={"part_number": part_number},
        content=data,
        headers={"Content-Type": "application/octet-stream"},
    )


def finish(session_id: str) -> Endpoint[UploadSession]:
    return Endpoint(HTTPMethod.POST, f"upload_sessions/{segment(session_id)}/finish", UploadSession)


def abort(session_id: str) -> Endpoint[UploadSession]:
    path = f"upload_sessions/{segment(session_id)}/abort"
    # violation(arch-3): POST abort discards uploaded parts
    return Endpoint(HTTPMethod.POST, path, UploadSession, effect=Effect.DESTRUCTIVE)


def abort_all() -> Endpoint[AbortActiveUploadsResult]:
    path = "upload_sessions/abort_active_uploads"
    # violation(arch-3): POST abort discards every upload
    return Endpoint(HTTPMethod.POST, path, AbortActiveUploadsResult, effect=Effect.DESTRUCTIVE)
