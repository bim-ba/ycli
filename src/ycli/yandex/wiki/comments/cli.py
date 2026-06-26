"""`wiki comments` commands."""
from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.wiki._clideps import wiki_client

app = typer.Typer(name="comments", help="Wiki page comments.", no_args_is_help=True)


@app.command("list")
def list_(
    ctx: typer.Context,
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
) -> None:
    """List comments on a page id (GET /pages/{id}/comments)."""
    client = wiki_client(ctx)
    print(client.comments.list(page_id=page_id).model_dump_json(by_alias=True))
