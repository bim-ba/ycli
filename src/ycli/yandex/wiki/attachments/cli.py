"""`wiki attachments` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.cliformat import output_format
from ycli.output import render

from ycli.yandex.wiki._clideps import wiki_client

app = typer.Typer(name="attachments", help="Wiki page attachments.", no_args_is_help=True)


@app.command("list")
def list_(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
) -> None:
    """List attachments on a page id (GET /pages/{id}/attachments)."""
    client = wiki_client(ctx)
    render(client.attachments.list(page_id=page_id), output_format=output_format(ctx))
