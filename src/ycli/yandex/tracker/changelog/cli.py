"""`tracker changelog` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker._types import (
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
    per_page: Annotated[int, typer.Option("--per-page", help="Entries per page.")] = 100,
) -> None:
    """List changelog entries for issue KEY."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.changelog.list(key, per_page=per_page), app_ctx.strategy, app_ctx.console
    )
