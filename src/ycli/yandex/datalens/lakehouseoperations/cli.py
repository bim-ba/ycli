"""`datalens lakehouseoperations` commands."""

from typing import Annotated

import typer

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import LakehouseOperation

app = typer.Typer(
    name="lakehouseoperations",
    help="DataLens Lakehouse operations (experimental in the API).",
    no_args_is_help=True,
)


@app.command(
    epilog="Experimental in the DataLens API and written from its document: not measured. "
    "An id nothing knows answers 403 Permission denied."
)
def get(
    operation_id: Annotated[str, typer.Argument(metavar="OPERATION_ID", help="Operation id.")],
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Print how far an operation is: done or not, its error or its response."""
    return datalens.lakehouseoperations.get(operation_id)
