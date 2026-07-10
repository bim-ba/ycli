"""`tracker users` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.pagination import resolve_cap

app = typer.Typer(name="users", help="Tracker organisation users.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(
    ctx: typer.Context,
    login_or_id: Annotated[
        str,
        typer.Argument(metavar="LOGIN_OR_ID", help="User login or uid (login:12345 if numeric)."),
    ],
    expand: Annotated[str, typer.Option(help="Extra data to include, e.g. groups.")] = "",
) -> None:
    """Get one user account by LOGIN_OR_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    user = app_ctx.tracker.users.get(login_or_id=login_or_id, expand=expand or None)
    Serializer.serialize(user, app_ctx.strategy, app_ctx.console)


@app.command("list")
def list_(
    ctx: typer.Context,
    limit: LimitOption = 0,
    all_: AllOption = False,
    expand: Annotated[str, typer.Option(help="Extra data to include, e.g. groups.")] = "",
) -> None:
    """List all organisation users (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(
        app_ctx.tracker.users.list(limit=cap, expand=expand or None),
        app_ctx.strategy,
        app_ctx.console,
    )
