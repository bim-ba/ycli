"""`wiki recovery` commands — restore a page deleted via `wiki pages delete`."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer

app = typer.Typer(
    name="recovery", help="Wiki page recovery (restore by token).", no_args_is_help=True
)


@app.command()
def restore(
    ctx: typer.Context,
    token: Annotated[
        str, typer.Argument(metavar="TOKEN", help="recovery_token from `wiki pages delete`.")
    ],
) -> None:
    """Restore a deleted page by its recovery TOKEN (POST /recovery_tokens/{token}/recover)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.wiki.recovery.restore(token=token), app_ctx.strategy, app_ctx.console
    )
