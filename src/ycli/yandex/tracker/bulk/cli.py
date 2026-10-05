"""`tracker bulk` commands: the status of a bulk change and the issues it failed on."""

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.bulk.models import BulkChange, BulkIssueResult
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="bulk", help="Tracker async bulk changes.", no_args_is_help=True)

BulkIDArg = Annotated[
    str, typer.Argument(metavar="BULK_ID", help="Bulk-change operation id from a trigger.")
]


@app.command()
def get(bulk_id: BulkIDArg, *, tracker: TrackerClient) -> BulkChange:
    """Print the current status of bulk-change BULK_ID (GET /bulkchange/{id})."""
    return tracker.bulk.get(bulk_id)


@app.command()
def issues_list(bulk_id: BulkIDArg, *, tracker: TrackerClient) -> ItemList[BulkIssueResult]:
    """List issues that a bulk change failed on (GET /bulkchange/{id}/issues)."""
    return tracker.bulk.issues_list(bulk_id)
