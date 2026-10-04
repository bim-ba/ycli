"""`tracker changelog` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.models import ItemList, SortDirection
from ycli.yandex.tracker.changelog.models import ChangelogEntry
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)

app = typer.Typer(name="changelog", help="Tracker issue changelog.", no_args_is_help=True)


@app.command("list")
def list_(
    key: KeyArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    field: Annotated[
        str | None, typer.Option(help="Only changes of this field, e.g. status.")
    ] = None,
    change_type: Annotated[
        str | None, typer.Option("--type", help="Only changes of this type, e.g. IssueWorkflow.")
    ] = None,
    sort: Annotated[str | None, values_option(SortDirection, help="Order of the changes.")] = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[ChangelogEntry]:
    """List all changelog entries for issue KEY (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.changelog.list(key, limit=cap, field=field, change_type=change_type, sort=sort)
