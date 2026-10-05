"""`wiki resources` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList, SortDirection
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.resources.models import ResourceItem, ResourceOrder

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
        str | None, values_option(ResourceOrder, "--order-by", help="Sort field.")
    ] = None,
    order_direction: Annotated[
        str | None,
        values_option(SortDirection, "--order-direction", help="Sort direction for --order-by."),
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
