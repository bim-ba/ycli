"""`wiki attachments` commands."""

from __future__ import annotations

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
