"""`datalens permissions` commands."""

from typing import Annotated

import typer

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.permissions.models import PermissionsBulk

app = typer.Typer(name="permissions", help="DataLens permissions.", no_args_is_help=True)


@app.command("get-bulk")
def get_bulk(
    entry_ids: Annotated[
        list[str] | None, typer.Option("--entry-id", help="An entry id (repeatable).")
    ] = None,
    workbook_ids: Annotated[
        list[str] | None, typer.Option("--workbook-id", help="A workbook id (repeatable).")
    ] = None,
    collection_ids: Annotated[
        list[str] | None, typer.Option("--collection-id", help="A collection id (repeatable).")
    ] = None,
    *,
    datalens: DataLensClient,
) -> PermissionsBulk:
    """Print what you may do with many entries, workbooks and collections at once.

    An object that does not exist answers `error: NOT_FOUND` under its id.
    """
    return datalens.permissions.get_bulk(
        entry_ids=entry_ids, workbook_ids=workbook_ids, collection_ids=collection_ids
    )
