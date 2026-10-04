"""`tracker links` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_argument
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.links.models import Link, LinkCreate, Relationship
from ycli.yandex.tracker.typedefs import (
    KeyArg,
)

app = typer.Typer(name="links", help="Tracker issue links.", no_args_is_help=True)


@app.command("list")
def list_(key: KeyArg, *, tracker: TrackerClient) -> ItemList[Link]:
    """List links for issue KEY."""
    return tracker.links.list(key)


@app.command()
def search(
    key: KeyArg,
    link_type: Annotated[
        list[str] | None,
        typer.Option(
            "--type",
            help="Keep only links with this relationship, e.g. relates (repeatable).",
        ),
    ] = None,
    field: Annotated[
        list[str] | None,
        typer.Option("--field", help="Field to include in each link (repeatable)."),
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[Link]:
    """List links of issue KEY, filtered and paged (POST …/links/_list; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.links.search(key, link_types=link_type, fields=field, limit=cap)


@app.command()
def add(
    key: KeyArg,
    relationship: Annotated[str, values_argument(Relationship, help="Relationship verb.")],
    target: Annotated[str, typer.Argument(help="Target issue key, e.g. DATAENGINEERING-2.")],
    *,
    tracker: TrackerClient,
) -> Link:
    """Link issue KEY to TARGET with RELATIONSHIP."""
    body = LinkCreate(relationship=relationship, issue=target)
    return tracker.links.add(key, body=body)


@app.command()
def delete(
    key: KeyArg,
    link_id: Annotated[str, typer.Argument(metavar="LINK_ID", help="Link id to remove.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete link LINK_ID from issue KEY."""
    tracker.links.delete(key, link_id)
    return Ack.deleted("link", link_id, on=key)
