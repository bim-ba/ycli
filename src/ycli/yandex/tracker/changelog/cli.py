"""`tracker changelog` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.models import SortDirection
from ycli.yandex.tracker.changelog.models import ChangelogEntry
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.typedefs import (
    IssueKeyArg,
)

app = typer.Typer(name="changelog", help="Tracker issue changelog.", no_args_is_help=True)


@app.command("list")
def list_(
    issue_key: IssueKeyArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    field: Annotated[
        str | None, typer.Option(help="Only changes of this field, e.g. status.")
    ] = None,
    change_type: Annotated[
        str | None,
        typer.Option("--change-type", help="Only changes of this type, e.g. IssueWorkflow."),
    ] = None,
    sort: Annotated[str | None, values_option(SortDirection, help="Order of the changes.")] = None,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> Listing[ChangelogEntry]:
    """List all changelog entries for issue ISSUE_KEY (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.changelog.list(
        issue_key, limit=cap, next=next_, field=field, change_type=change_type, sort=sort
    )
