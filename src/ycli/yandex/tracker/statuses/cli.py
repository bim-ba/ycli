"""`tracker statuses` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import values_option
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.models import LocalizedName
from ycli.yandex.tracker.statuses.models import Status, StatusCreate, StatusType, StatusUpdate

app = typer.Typer(name="statuses", help="Tracker issue statuses.", no_args_is_help=True)


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[Status]:
    """List all issue statuses."""
    return tracker.statuses.list()


@app.command()
def create(
    key: Annotated[str, typer.Option(help="Key of the new status (Latin, lower-case start).")],
    type_: Annotated[str, values_option(StatusType, "--type", help="Status type.")],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="Status name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="Status name in English.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Status:
    """Create an issue status (POST /statuses/)."""
    body = StatusCreate(
        key=key,
        name=LocalizedName(ru=name_ru, en=name_en),
        type=type_,
    )
    return tracker.statuses.create(body)


@app.command()
def update(
    status_id: Annotated[str, typer.Argument(metavar="STATUS_ID", help="Status id or key.")],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="New status name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="New status name in English.")
    ] = None,
    description: Annotated[str | None, typer.Option(help="New status description.")] = None,
    type_: Annotated[
        str | None, values_option(StatusType, "--type", help="New status type.")
    ] = None,
    order: Annotated[int | None, typer.Option(help="New display-order weight.")] = None,
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Status:
    """Edit issue status STATUS_ID (PATCH /statuses/{id}?version=)."""
    named = name_ru is not None or name_en is not None
    body = StatusUpdate(
        name=LocalizedName(ru=name_ru, en=name_en) if named else None,
        description=description,
        type=type_,
        order=order,
    )
    return tracker.statuses.update(status_id, body, version=version)
