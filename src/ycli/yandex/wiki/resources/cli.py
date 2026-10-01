"""`wiki resources` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.resources.models import ResourceItemList

app = typer.Typer(
    name="resources", help="Wiki page resources (attachments + grids).", no_args_is_help=True
)


@app.command("list")
def list_(
    page_id: Annotated[int, typer.Argument(metavar="PAGE_ID", help="Numeric page id.")],
    limit: LimitOption = 0,
    all_: AllOption = False,
    q: Annotated[str, typer.Option("--q", help="Title search filter.")] = "",
    types: Annotated[
        str, typer.Option("--types", help="Comma-separated kinds: attachment,grid.")
    ] = "",
    order_by: Annotated[
        str, typer.Option("--order-by", help="Sort field: name_title or created_at.")
    ] = "",
    *,
    config: AppConfig,
    wiki: WikiClient,
) -> ResourceItemList:
    """List a page's resources — attachments and grids (GET /pages/{id}/resources)."""
    cap = resolve_cap(limit, config.http.max_items, all_=all_)
    return wiki.resources.list(
        page_id=page_id, limit=cap, q=q or None, types=types or None, order_by=order_by or None
    )
