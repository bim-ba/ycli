"""`tracker attachments` commands (list renders; download/thumbnail write raw bytes)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.binary import write_output
from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="attachments", help="Tracker issue attachments.", no_args_is_help=True)

_ISSUE = typer.Argument(metavar="ISSUE", help="Issue key or id, e.g. JUNE-2.")
_FILE_ID = typer.Argument(metavar="FILE_ID", help="Attachment file id.")
_OUTPUT = typer.Option("--output", "-O", help="Write to this path; omit or '-' for stdout.")


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    issue_key: Annotated[str, _ISSUE],
) -> None:
    """List files attached to an issue (GET /issues/{issue}/attachments)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.attachments.list(issue_key), app_ctx.strategy, app_ctx.console
    )


@app.command("download")
def download(
    ctx: typer.Context,
    issue_key: Annotated[str, _ISSUE],
    file_id: Annotated[str, _FILE_ID],
    filename: Annotated[str, typer.Argument(metavar="FILENAME", help="Attachment file name.")],
    output: Annotated[str | None, _OUTPUT] = None,
) -> None:
    """Download an attachment's raw bytes to --output (or stdout). Binary is CLI/SDK-only."""
    app_ctx = AppContext.from_typer_context(ctx)
    write_output(app_ctx.tracker.attachments.download(issue_key, file_id, filename), output)


@app.command("thumbnail")
def thumbnail(
    ctx: typer.Context,
    issue_key: Annotated[str, _ISSUE],
    file_id: Annotated[str, _FILE_ID],
    output: Annotated[str | None, _OUTPUT] = None,
) -> None:
    """Download a graphic attachment's preview thumbnail to --output (or stdout)."""
    app_ctx = AppContext.from_typer_context(ctx)
    write_output(app_ctx.tracker.attachments.download_thumbnail(issue_key, file_id), output)
