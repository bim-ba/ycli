"""`wiki resources` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.resources.models import ResourceItem

app = typer.Typer(
    name="resources", help="Wiki page resources (attachments + grids).", no_args_is_help=True
)


@app.command("list")
def list_(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: LimitOption = None,
    all_: AllOption = False,
    q: Annotated[str | None, typer.Option("--q", help="Title search filter.")] = None,
    types: Annotated[
        str | None, typer.Option("--types", help="Comma-separated kinds: attachment,grid.")
    ] = None,
    order_by: Annotated[
        str | None, typer.Option("--order-by", help="Sort field: name_title or created_at.")
    ] = None,
    order_direction: Annotated[
        str | None,
        typer.Option("--order-direction", help="Sort direction for --order-by: asc or desc."),
    ] = None,
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ItemList[ResourceItem]:
    """List a page's resources — attachments and grids (GET /pages/{id}/resources)."""
    cap = config.http.cap(limit, all_=all_)
    return wiki.resources.list(
        page_id=page_id,
        limit=cap,
        q=q,
        types=types,
        order_by=order_by,
        order_direction=order_direction,
    )
