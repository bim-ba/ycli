"""`datalens workbookimports` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.body_fields import CallerFields
from ycli.cli.progress import wait_for
from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.schemas.workbook_import import StartWorkbookImportArgs
from ycli.yandex.datalens.workbookimports.models import (
    WorkbookImportStarted,
    WorkbookImportStatus,
)

app = typer.Typer(
    name="workbookimports", help="Imports of a DataLens workbook.", no_args_is_help=True
)


@app.command()
def start(
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            help="The `data` of an export's result, as a JSON object; --body-file gives it "
            "under `data`.",
        ),
    ] = None,
    title: Annotated[
        str | None, typer.Option("--title", help="The title of the new workbook.")
    ] = None,
    collection_id: Annotated[
        str | None,
        typer.Option("--collection-id", help="The collection to make it in; the root if not."),
    ] = None,
    description: Annotated[
        str | None, typer.Option("--description", help="The description of the new workbook.")
    ] = None,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status before printing.")
    ] = True,
    *,
    caller: CallerFields,
    config: AppConfig,
    datalens: DataLensClient,
) -> WorkbookImportStarted | WorkbookImportStatus:
    """Make a workbook from an export (async): prints the import's final status.

    With --no-wait it prints the ids of the import and of the workbook at once.

    `ycli datalens workbookexports result-get EXPORT_ID | jq '{data}' > export.json` writes
    the file --body-file takes here.
    """
    given = {
        "data": None if data is None else json.loads(data),
        "title": title,
        "collectionId": collection_id,
        "description": description,
    }
    # `data` usually comes from --body-file: merge before the model is built. A workbook with
    # no collection named goes to the root, which the API takes as an explicit null.
    flags = {key: value for key, value in given.items() if value is not None}
    body = StartWorkbookImportArgs.model_validate({"collectionId": None, **caller.over(flags)})
    started = datalens.workbookimports.start(
        body.data,
        title=body.title,
        collection_id=body.collection_id,
        description=body.description,
    )
    if wait and started.import_id is not None:
        import_id = started.import_id
        return wait_for(
            lambda: datalens.workbookimports.status_get(import_id),
            lambda state: state.status is not None and state.status.root != "pending",
            message="Waiting for the workbook import…",
            max_wait_seconds=config.http.max_wait_seconds,
        )
    return started


@app.command("status-get")
def status_get(
    import_id: Annotated[str, typer.Argument(metavar="IMPORT_ID", help="Import id.")],
    *,
    datalens: DataLensClient,
) -> WorkbookImportStatus:
    """Print how far an import is: pending, success or error, with its notifications."""
    return datalens.workbookimports.status_get(import_id)
