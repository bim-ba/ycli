"""`tracker attachments` commands (list renders; download/thumbnail write raw bytes)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.yandex.tracker.attachments.models import AttachmentList
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="attachments", help="Tracker issue attachments.", no_args_is_help=True)

_ISSUE = typer.Argument(metavar="ISSUE", help="Issue key or id, e.g. JUNE-2.")
_FILE_ID = typer.Argument(metavar="FILE_ID", help="Attachment file id.")
_OUTPUT = typer.Option("--output", "-O", help="Write to this path; omit or '-' for stdout.")


@app.command("list")
def list_(issue_key: Annotated[str, _ISSUE], *, tracker: TrackerClient) -> AttachmentList:
    """List files attached to an issue (GET /issues/{issue}/attachments)."""
    return tracker.attachments.list(issue_key)


@app.command("download")
def download(
    issue_key: Annotated[str, _ISSUE],
    file_id: Annotated[str, _FILE_ID],
    filename: Annotated[str, typer.Argument(metavar="FILENAME", help="Attachment file name.")],
    output: Annotated[str | None, _OUTPUT] = None,
    *,
    tracker: TrackerClient,
) -> BinaryResult:
    """Download an attachment's raw bytes to --output (or stdout). Binary is CLI/SDK-only."""
    return BinaryResult(tracker.attachments.download(issue_key, file_id, filename), output)


@app.command("thumbnail")
def thumbnail(
    issue_key: Annotated[str, _ISSUE],
    file_id: Annotated[str, _FILE_ID],
    output: Annotated[str | None, _OUTPUT] = None,
    *,
    tracker: TrackerClient,
) -> BinaryResult:
    """Download a graphic attachment's preview thumbnail to --output (or stdout)."""
    return BinaryResult(tracker.attachments.download_thumbnail(issue_key, file_id), output)
