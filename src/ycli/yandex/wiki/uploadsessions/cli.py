"""`wiki uploadsessions` commands — the low-level binary upload pipeline.

``create`` → ``upload-part`` (repeat per part) → ``finish``, then attach the file with
``wiki attachments attach`` / ``wiki attachments upload``. ``abort`` / ``abort-all`` cancel.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.wiki.uploadsessions.models import UploadSessionCreate

app = typer.Typer(
    name="uploadsessions",
    help="Wiki file upload sessions (the binary upload pipeline).",
    no_args_is_help=True,
)

SessionIdArg = Annotated[
    str, typer.Argument(metavar="SESSION_ID", help="UUID4 of the upload session.")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def create(
    ctx: typer.Context,
    file_name: Annotated[str, typer.Option(help="Name to give the uploaded file.")],
    file_size: Annotated[int, typer.Option(help="Total file size in bytes (sum of all parts).")],
) -> None:
    """Open an upload session (POST /upload_sessions)."""
    app_ctx = AppContext.from_typer_context(ctx)
    body = UploadSessionCreate(file_name=file_name, file_size=file_size)
    Serializer.serialize(
        app_ctx.wiki.uploadsessions.create(body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def get(ctx: typer.Context, session_id: SessionIdArg) -> None:
    """Get an upload session's current state (GET /upload_sessions/{session_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.uploadsessions.get(session_id=session_id), app_ctx.strategy, app_ctx.console
    )


@app.command("upload-part")
def upload_part(
    ctx: typer.Context,
    session_id: SessionIdArg,
    file_path: Annotated[
        str, typer.Argument(metavar="FILE_PATH", help="Path to the file part's bytes to upload.")
    ],
    part_number: Annotated[
        int, typer.Option(help="1-based part index (1 for the first part, +1 per next part).")
    ] = 1,
) -> None:
    """Upload one octet-stream part from FILE_PATH (PUT .../{session_id}/upload_part)."""
    app_ctx = AppContext.from_typer_context(ctx)
    data = Path(file_path).read_bytes()
    Serializer.serialize(
        app_ctx.wiki.uploadsessions.upload_part(session_id, part_number=part_number, data=data),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def finish(ctx: typer.Context, session_id: SessionIdArg) -> None:
    """Finish an upload session (POST /upload_sessions/{session_id}/finish)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.uploadsessions.finish(session_id=session_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def abort(ctx: typer.Context, session_id: SessionIdArg) -> None:
    """Abort one upload session (POST /upload_sessions/{session_id}/abort)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.uploadsessions.abort(session_id=session_id), app_ctx.strategy, app_ctx.console
    )


@app.command("abort-all")
def abort_all(ctx: typer.Context) -> None:
    """Abort ALL active upload sessions to free quota (POST .../abort_active_uploads)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.wiki.uploadsessions.abort_all(), app_ctx.strategy, app_ctx.console)
