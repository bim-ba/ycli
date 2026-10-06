"""`datalens workbookexports` commands."""

from typing import Annotated

import typer

from ycli.cli.progress import wait_for
from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.workbookexports.models import (
    WorkbookExport,
    WorkbookExportCancelled,
    WorkbookExportStarted,
    WorkbookExportStatus,
)

app = typer.Typer(
    name="workbookexports", help="Exports of a DataLens workbook.", no_args_is_help=True
)

ExportIDArg = Annotated[str, typer.Argument(metavar="EXPORT_ID", help="Export id.")]


@app.command()
def start(
    workbook_id: Annotated[str, typer.Argument(metavar="WORKBOOK_ID", help="Workbook id.")],
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> WorkbookExportStarted | WorkbookExportStatus:
    """Export a workbook (async): prints the export's final status, or with --no-wait its id.

    `workbookexports result-get EXPORT_ID` then prints the exported workbook.
    """
    started = datalens.workbookexports.start(workbook_id)
    if wait and started.export_id is not None:
        export_id = started.export_id
        return wait_for(
            lambda: datalens.workbookexports.status_get(export_id),
            lambda state: state.status is not None and state.status.root != "pending",
            message="Waiting for the workbook export…",
            max_wait_seconds=config.http.max_wait_seconds,
        )
    return started


@app.command("status-get")
def status_get(export_id: ExportIDArg, *, datalens: DataLensClient) -> WorkbookExportStatus:
    """Print how far an export is: pending, success or error, with its notifications."""
    return datalens.workbookexports.status_get(export_id)


@app.command("result-get")
def result_get(export_id: ExportIDArg, *, datalens: DataLensClient) -> WorkbookExport:
    """Print the exported workbook; its `data` is what `workbookimports start` takes.

    An export that is not over, or was cancelled, answers 409.
    """
    return datalens.workbookexports.result_get(export_id)


@app.command()
def cancel(export_id: ExportIDArg, *, datalens: DataLensClient) -> WorkbookExportCancelled:
    """Stop an export; one that is over answers the same."""
    return datalens.workbookexports.cancel(export_id)
