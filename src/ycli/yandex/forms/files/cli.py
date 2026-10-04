"""`forms files` commands (form-filling file storage).

upload / download move raw bytes (binary payloads), so they are CLI/SDK-only; verify and delete
also ship as MCP tools (``files_verify`` / ``files_delete``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.files.models import FileIn
from ycli.yandex.forms.models import FileOut
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,
)
from ycli.yandex.models import Ack, ItemList

app = typer.Typer(name="files", help="Forms form-filling file storage.", no_args_is_help=True)

_PATH = typer.Option("--path", help="File download path (from an upload response).")
_URL = typer.Option("--url", help="File download URL (from an upload response).")
# Module-level Annotated alias so ``Path`` is referenced at runtime (typer resolves annotations
# via get_type_hints), keeping the import out of a TYPE_CHECKING block.
FilePathArg = Annotated[
    Path,
    typer.Argument(
        exists=True,
        dir_okay=False,
        readable=True,
        metavar="FILE_PATH",
        help="Local file to upload.",
    ),
]


@app.command()
def upload(survey_id: SurveyIdArg, file_path: FilePathArg, *, forms: FormsClient) -> FileOut:
    """Upload a file for form filling (POST …/files) — needs external storage on the form."""
    return forms.files.upload(survey_id, filename=file_path.name, data=file_path.read_bytes())


@app.command()
def verify(
    survey_id: SurveyIdArg,
    path: Annotated[
        list[str] | None, typer.Option("--path", help="File path to check (repeatable).")
    ] = None,
    url: Annotated[
        list[str] | None,
        typer.Option("--url", help="File URL to check (repeatable, paired to --path)."),
    ] = None,
    *,
    forms: FormsClient,
) -> ItemList[FileOut]:
    """Check upload status / access of already-uploaded files (POST …/files/verify)."""
    paths = path or []
    urls = url or []
    if not paths and not urls:
        raise typer.BadParameter("pass at least one --path (or --url)")
    if urls and len(urls) != len(paths):
        raise typer.BadParameter("--url count must match --path count")
    files = [
        FileIn(path=p or None, url=(urls[index] if index < len(urls) else None) or None)
        for index, p in enumerate(paths or urls)
    ]
    return forms.files.verify(survey_id, files)


@app.command()
def download(
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
        str | None,
        typer.Option("--hash", help="Access hash from the upload response (anonymous download)."),
    ] = None,
    *,
    forms: FormsClient,
) -> BinaryResult:
    """Download a stored file's raw bytes to --output (or stdout). Binary is CLI/SDK-only."""
    data = forms.files.download(path, download=disposition, file_hash=file_hash)
    return BinaryResult(data, output)


@app.command()
def delete(
    path: Annotated[str | None, _PATH] = None,
    url: Annotated[str | None, _URL] = None,
    *,
    forms: FormsClient,
) -> Ack:
    """Delete a stored file by --path and/or --url (DELETE /files)."""
    if path is None and url is None:
        raise typer.BadParameter("pass --path and/or --url")
    return forms.files.delete(path=path, url=url)
