"""`tracker changelog` commands."""

from __future__ import annotations

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.typedefs import (
    KeyArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="changelog", help="Tracker issue changelog.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    key: KeyArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
) -> None:
    """List all changelog entries for issue KEY (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(
        app_ctx.tracker.changelog.list(key, limit=cap), app_ctx.strategy, app_ctx.console
    )
