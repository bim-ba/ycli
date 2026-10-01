"""`tracker changelog` commands."""

from __future__ import annotations

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.pagination import resolve_cap
from ycli.yandex.tracker.changelog.models import ChangelogList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)

app = typer.Typer(name="changelog", help="Tracker issue changelog.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    key: KeyArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ChangelogList:
    """List all changelog entries for issue KEY (auto-paginated; --all for everything)."""
    cap = resolve_cap(limit, config.http.max_items, all_=all_)
    return tracker.changelog.list(key, limit=cap)
