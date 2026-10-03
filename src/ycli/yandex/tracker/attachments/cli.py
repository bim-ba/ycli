"""`tracker attachments` commands (reads render; the downloads write raw bytes)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="attachments", help="Tracker issue attachments.", no_args_is_help=True)

_ISSUE = typer.Argument(metavar="ISSUE", help="Issue key or id, e.g. JUNE-2.")
_FILE_ID = typer.Argument(metavar="FILE_ID", help="Attachment file id.")
_OUTPUT = typer.Option("--output", "-O", help="Write to this path; omit or '-' for stdout.")
_RENAME_TO = typer.Option("--rename-to", help="Store the file under this name instead of its own.")
# Module-level Annotated alias so ``Path`` is referenced at runtime (typer resolves annotations
# via get_type_hints), keeping the import out of a TYPE_CHECKING block.
FilePathArg = Annotated[Path, typer.Argument(metavar="FILE_PATH", help="Local file to upload.")]


@app.command("list")
def list_(issue_key: Annotated[str, _ISSUE], *, tracker: TrackerClient) -> ItemList[Attachment]:
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


@app.command("download-thumbnail")
def download_thumbnail(
    issue_key: Annotated[str, _ISSUE],
    file_id: Annotated[str, _FILE_ID],
    output: Annotated[str | None, _OUTPUT] = None,
    *,
    tracker: TrackerClient,
) -> BinaryResult:
    """Download a graphic attachment's preview thumbnail to --output (or stdout)."""
    return BinaryResult(tracker.attachments.download_thumbnail(issue_key, file_id), output)


@app.command()
def get(
    issue_key: Annotated[str, _ISSUE],
    file_id: Annotated[str, _FILE_ID],
    *,
    tracker: TrackerClient,
) -> Attachment:
    """Print an attachment's metadata (GET /issues/{issue}/attachments/{file_id})."""
    return tracker.attachments.get(issue_key, file_id)


@app.command()
def delete(
    issue_key: Annotated[str, _ISSUE],
    file_id: Annotated[str, _FILE_ID],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete an attachment from an issue (DELETE /issues/{issue}/attachments/{file_id})."""
    tracker.attachments.delete(issue_key, file_id)
    return Ack.deleted("attachment", file_id, on=issue_key)


@app.command()
def upload(
    issue_key: Annotated[str, _ISSUE],
    file_path: FilePathArg,
    rename_to: Annotated[str | None, _RENAME_TO] = None,
    *,
    tracker: TrackerClient,
) -> Attachment:
    """Attach a local file to an issue (POST /issues/{issue}/attachments)."""
    return tracker.attachments.upload(
        issue_key,
        filename=file_path.name,
        data=file_path.read_bytes(),
        rename_to=rename_to,
    )


@app.command("upload-temp")
def upload_temp(
    file_path: FilePathArg,
    rename_to: Annotated[str | None, _RENAME_TO] = None,
    *,
    tracker: TrackerClient,
) -> Attachment:
    """Upload a temporary file (POST /attachments); its id attaches once to an issue or comment."""
    return tracker.attachments.upload_temp(
        filename=file_path.name, data=file_path.read_bytes(), rename_to=rename_to
    )
