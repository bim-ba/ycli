"""`wiki attachments` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.binary import write_output
from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="attachments", help="Wiki page attachments.", no_args_is_help=True)

OutputOption = Annotated[
    str | None,
    typer.Option("--output", help="Write bytes to this path; omit / '-' streams to stdout."),
]


@app.command("list")
def list_(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: Annotated[int, typer.Option(help="Max attachments (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every attachment (no cap).")] = False,
) -> None:
    """List attachments on a page id (GET /pages/{id}/attachments; auto-paginated)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.wiki.attachments.list(page_id=page_id, limit=cap), app_ctx.strategy, app_ctx.console
    )


@app.command()
def download(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_id: Annotated[int, typer.Argument(metavar="FILE_ID", help="Numeric attachment id.")],
    output: OutputOption = None,
) -> None:
    """Download an attachment by id to --output (or stdout) as raw bytes."""
    app_ctx = AppContext.from_typer_context(ctx)
    write_output(app_ctx.wiki.attachments.download(page_id=page_id, file_id=file_id), output)


@app.command("download-by-url")
def download_by_url(
    ctx: typer.Context,
    url: Annotated[
        str, typer.Argument(metavar="URL", help="Page-slug URL: <slug>/.files/<filename>.")
    ],
    output: OutputOption = None,
) -> None:
    """Download an attachment by page-slug URL to --output (or stdout) as raw bytes."""
    app_ctx = AppContext.from_typer_context(ctx)
    write_output(app_ctx.wiki.attachments.download_by_url(url=url), output)


@app.command()
def delete(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_id: Annotated[int, typer.Argument(metavar="FILE_ID", help="Numeric attachment id.")],
) -> None:
    """Delete an attachment by id (DELETE /pages/{id}/attachments/{file_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.wiki.attachments.delete(page_id=page_id, file_id=file_id)
    print(f"Deleted attachment {file_id} from page {page_id}.")


@app.command()
def attach(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    session: Annotated[
        list[str],
        typer.Option("--session", help="Finished upload-session id to attach (repeatable)."),
    ],
) -> None:
    """Attach uploaded file(s) to a page by upload-session id (POST /pages/{id}/attachments)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.attachments.attach(page_id, session), app_ctx.strategy, app_ctx.console
    )


@app.command()
def upload(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    file_path: Annotated[
        str, typer.Argument(metavar="FILE_PATH", help="Path to the local file to upload + attach.")
    ],
) -> None:
    """Upload a local file and attach it to a page in one step (create→upload→finish→attach)."""
    app_ctx = AppContext.from_typer_context(ctx)
    path = Path(file_path)
    result = app_ctx.wiki.attachments.upload(
        app_ctx.wiki.uploadsessions,
        page_id,
        file_name=path.name,
        data=path.read_bytes(),
    )
    Serializer.serialize(result, app_ctx.strategy, app_ctx.console)
