"""`wiki resources` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.pagination import resolve_cap

app = typer.Typer(
    name="resources", help="Wiki page resources (attachments + grids).", no_args_is_help=True
)


@app.command("list")
def list_(
    ctx: typer.Context,
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
) -> None:
    """List a page's resources — attachments and grids (GET /pages/{id}/resources)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(
        app_ctx.wiki.resources.list(
            page_id=page_id, limit=cap, q=q or None, types=types or None, order_by=order_by or None
        ),
        app_ctx.strategy,
        app_ctx.console,
    )
