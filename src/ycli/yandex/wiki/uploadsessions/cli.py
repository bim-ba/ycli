"""`wiki uploadsessions` commands — the low-level binary upload pipeline.

``create`` → ``upload-part`` (repeat per part) → ``finish``, then attach the file with
``wiki attachments attach`` / ``wiki attachments upload``. ``abort`` / ``abort-all`` cancel.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.uploadsessions.models import (
    AbortActiveUploadsResult,
    UploadSession,
    UploadSessionCreate,
)

app = typer.Typer(
    name="uploadsessions",
    help="Wiki file upload sessions (the binary upload pipeline).",
    no_args_is_help=True,
)

SessionIDArg = Annotated[
    str, typer.Argument(metavar="SESSION_ID", help="UUID4 of the upload session.")
]


@app.command()
def create(
    file_name: Annotated[str, typer.Option(help="Name to give the uploaded file.")],
    file_size: Annotated[int, typer.Option(help="Total file size in bytes (sum of all parts).")],
    *,
    wiki: WikiClient,
) -> UploadSession:
    """Open an upload session (POST /upload_sessions)."""
    body = UploadSessionCreate(file_name=file_name, file_size=file_size)
    return wiki.uploadsessions.create(body)


@app.command()
def get(session_id: SessionIDArg, *, wiki: WikiClient) -> UploadSession:
    """Get an upload session's current state (GET /upload_sessions/{session_id})."""
    return wiki.uploadsessions.get(session_id=session_id)


@app.command("upload-part")
def upload_part(
    session_id: SessionIDArg,
    file_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            metavar="FILE_PATH",
            help="Path to the file part's bytes to upload.",
        ),
    ],
    part_number: Annotated[
        int, typer.Option(help="1-based part index (1 for the first part, +1 per next part).")
    ] = 1,
    *,
    wiki: WikiClient,
) -> UploadSession:
    """Upload one octet-stream part from FILE_PATH (PUT .../{session_id}/upload_part)."""
    data = file_path.read_bytes()
    return wiki.uploadsessions.upload_part(session_id, part_number=part_number, data=data)


@app.command()
def finish(session_id: SessionIDArg, *, wiki: WikiClient) -> UploadSession:
    """Finish an upload session (POST /upload_sessions/{session_id}/finish)."""
    return wiki.uploadsessions.finish(session_id=session_id)


@app.command()
def abort(session_id: SessionIDArg, *, wiki: WikiClient) -> UploadSession:
    """Abort one upload session (POST /upload_sessions/{session_id}/abort)."""
    return wiki.uploadsessions.abort(session_id=session_id)


@app.command("abort-all")
def abort_all(*, wiki: WikiClient) -> AbortActiveUploadsResult:
    """Abort ALL active upload sessions to free quota (POST .../abort_active_uploads)."""
    return wiki.uploadsessions.abort_all()
