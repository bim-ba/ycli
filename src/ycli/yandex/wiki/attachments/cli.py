"""`wiki attachments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(name="attachments", help="Wiki page attachments.", no_args_is_help=True)


@app.command("list")
def list_(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
) -> None:
    """List attachments on a page id (GET /pages/{id}/attachments)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.attachments.list(page_id=page_id), app_ctx.strategy, app_ctx.console
    )
