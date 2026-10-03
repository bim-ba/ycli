"""`tracker users` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.users.models import User

app = typer.Typer(name="users", help="Tracker organisation users.", no_args_is_help=True)


@app.command()
def get(
    login_or_id: Annotated[
        str,
        typer.Argument(metavar="LOGIN_OR_ID", help="User login or uid (login:12345 if numeric)."),
    ],
    expand: Annotated[str, typer.Option(help="Extra data to include, e.g. groups.")] = "",
    *,
    tracker: TrackerClient,
) -> User:
    """Get one user account by LOGIN_OR_ID."""
    return tracker.users.get(login_or_id=login_or_id, expand=expand or None)


@app.command("list")
def list_(
    limit: LimitOption = 0,
    all_: AllOption = False,
    expand: Annotated[str, typer.Option(help="Extra data to include, e.g. groups.")] = "",
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[User]:
    """List all organisation users (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.users.list(limit=cap, expand=expand or None)
