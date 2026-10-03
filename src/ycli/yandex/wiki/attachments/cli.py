"""`wiki attachments` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.wiki.attachments.models import AttachedFile, Attachment
from ycli.yandex.wiki.client import WikiClient

app = typer.Typer(name="attachments", help="Wiki page attachments.", no_args_is_help=True)

OutputOption = Annotated[
    str | None,
    typer.Option("--output", help="Write bytes to this path; omit / '-' streams to stdout."),
]


@app.command("list")
def list_(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: LimitOption = None,
    all_: AllOption = False,
    order_by: Annotated[
        str | None, typer.Option("--order-by", help="Sort field: name, size or created_at.")
    ] = None,
    order_direction: Annotated[
        str | None,
        typer.Option("--order-direction", help="Sort direction for --order-by: asc or desc."),
    ] = None,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[Attachment]:
    """List attachments on a page id (GET /pages/{id}/attachments; auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.attachments.list(
        page_id=page_id,
        limit=cap,
        order_by=order_by,
        order_direction=order_direction,
    )


@app.command()
def get(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_id: Annotated[int, typer.Argument(metavar="FILE_ID", help="Numeric attachment id.")],
    *,
    wiki: WikiClient,
) -> AttachedFile:
    """Show one attachment's metadata (GET /pages/{id}/attachments/{file_id}); undocumented API."""
    return wiki.attachments.get(page_id=page_id, file_id=file_id)


@app.command()
def preview(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_id: Annotated[int, typer.Argument(metavar="FILE_ID", help="Numeric attachment id.")],
    output: OutputOption = None,
    *,
    wiki: WikiClient,
) -> BinaryResult:
    """Save an attachment's preview image to --output (or stdout); undocumented API.

    A file with no preview (``attachments get`` says ``has_preview: false``) comes back as the
    base64 text of a 1-pixel PNG, not an image.
    """
    return BinaryResult(wiki.attachments.preview(page_id=page_id, file_id=file_id), output)


@app.command()
def download(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_id: Annotated[int, typer.Argument(metavar="FILE_ID", help="Numeric attachment id.")],
    output: OutputOption = None,
    *,
    wiki: WikiClient,
) -> BinaryResult:
    """Download an attachment by id to --output (or stdout) as raw bytes."""
    return BinaryResult(wiki.attachments.download(page_id=page_id, file_id=file_id), output)


@app.command("download-by-url")
def download_by_url(
    url: Annotated[
        str, typer.Argument(metavar="URL", help="Page-slug URL: <slug>/.files/<filename>.")
    ],
    output: OutputOption = None,
    *,
    wiki: WikiClient,
) -> BinaryResult:
    """Download an attachment by page-slug URL to --output (or stdout) as raw bytes."""
    return BinaryResult(wiki.attachments.download_by_url(url=url), output)


@app.command()
def delete(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_id: Annotated[int, typer.Argument(metavar="FILE_ID", help="Numeric attachment id.")],
    *,
    wiki: WikiClient,
) -> Ack:
    """Delete an attachment by id (DELETE /pages/{id}/attachments/{file_id})."""
    wiki.attachments.delete(page_id=page_id, file_id=file_id)
    return Ack.deleted("attachment", file_id, from_=f"page {page_id}")


@app.command()
def attach(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    session: Annotated[
        list[str],
        typer.Option("--session", help="Finished upload-session id to attach (repeatable)."),
    ],
    *,
    wiki: WikiClient,
) -> ItemList[AttachedFile]:
    """Attach uploaded file(s) to a page by upload-session id (POST /pages/{id}/attachments)."""
    return wiki.attachments.attach(page_id, session)


@app.command()
def upload(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_path: Annotated[
        str, typer.Argument(metavar="FILE_PATH", help="Path to the local file to upload + attach.")
    ],
    *,
    wiki: WikiClient,
) -> ItemList[AttachedFile]:
    """Upload a local file and attach it to a page in one step (create→upload→finish→attach)."""
    path = Path(file_path)
    result = wiki.attachments.upload(
        wiki.uploadsessions,
        page_id,
        file_name=path.name,
        data=path.read_bytes(),
    )
    return result
