"""`wiki comments` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.context import AppContext
from ycli.output import Serializer

app = typer.Typer(name="comments", help="Wiki page comments.", no_args_is_help=True)


@app.command("list")
def list_(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
) -> None:
    """List comments on a page id (GET /pages/{id}/comments)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.comments.list(page_id=page_id), app_ctx.strategy, app_ctx.console
    )
