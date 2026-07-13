"""`forms files` commands (form-filling file storage).

upload / download move raw bytes (binary payloads), so they are CLI/SDK-only; verify and delete
also ship as MCP tools (``files_verify`` / ``files_delete``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.binary import write_output
from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.files.models import FileIn
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="files", help="Forms form-filling file storage.", no_args_is_help=True)

_PATH = typer.Option("--path", help="File download path (from an upload response).")
_URL = typer.Option("--url", help="File download URL (from an upload response).")
# Module-level Annotated alias so ``Path`` is referenced at runtime (typer resolves annotations
# via get_type_hints), keeping the import out of a TYPE_CHECKING block.
FilePathArg = Annotated[Path, typer.Argument(metavar="FILE_PATH", help="Local file to upload.")]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def upload(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    file_path: FilePathArg,
) -> None:
    """Upload a file for form filling (POST …/files) — needs external storage on the form."""
    app_ctx = AppContext.from_typer_context(ctx)
    result = app_ctx.forms.files.upload(
        survey_id, filename=file_path.name, data=file_path.read_bytes()
    )
    Serializer.serialize(result, app_ctx.strategy, app_ctx.console)


@app.command()
def verify(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    path: Annotated[
        list[str] | None, typer.Option("--path", help="File path to check (repeatable).")
    ] = None,
    url: Annotated[
        list[str] | None,
        typer.Option("--url", help="File URL to check (repeatable, paired to --path)."),
    ] = None,
) -> None:
    """Check upload status / access of already-uploaded files (POST …/files/verify)."""
    paths = path or []
    urls = url or []
    if not paths and not urls:
        raise typer.BadParameter("pass at least one --path (or --url)")
    if urls and len(urls) != len(paths):
        raise typer.BadParameter("--url count must match --path count")
    files = [
        FileIn(path=p or None, url=(urls[index] if index < len(urls) else None))
        for index, p in enumerate(paths or urls)
    ]
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.files.verify(survey_id, files), app_ctx.strategy, app_ctx.console
    )


@app.command()
def download(
    ctx: typer.Context,
    path: Annotated[str, _PATH],
    output: Annotated[
        str | None,
        typer.Option("--output", "-O", help="Write to this path; omit or '-' for stdout."),
    ] = None,
    disposition: Annotated[
        bool,
        typer.Option("--download", help="Ask the API for a Content-Disposition filename header."),
    ] = False,
    file_hash: Annotated[
        str,
        typer.Option("--hash", help="Access hash from the upload response (anonymous download)."),
    ] = "",
) -> None:
    """Download a stored file's raw bytes to --output (or stdout). Binary is CLI/SDK-only."""
    app_ctx = AppContext.from_typer_context(ctx)
    data = app_ctx.forms.files.download(path, download=disposition, file_hash=file_hash or None)
    write_output(data, output)


@app.command()
def delete(
    ctx: typer.Context,
    path: Annotated[str, _PATH] = "",
    url: Annotated[str, _URL] = "",
) -> None:
    """Delete a stored file by --path and/or --url (DELETE /files)."""
    if not path and not url:
        raise typer.BadParameter("pass --path and/or --url")
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.files.delete(path=path or None, url=url or None),
        app_ctx.strategy,
        app_ctx.console,
    )
