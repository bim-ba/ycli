"""`wiki attachments` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.wiki._clideps import wiki_client

app = typer.Typer(name="attachments", help="Wiki page attachments.", no_args_is_help=True)


@app.command("list")
def list_(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
) -> None:
    """List attachments on a page id (GET /pages/{id}/attachments)."""
    client = wiki_client(ctx)
    print(client.attachments.list(page_id=page_id).model_dump_json(by_alias=True))
