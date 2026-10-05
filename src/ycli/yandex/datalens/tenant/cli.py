"""`datalens tenant` commands."""

import typer

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.tenant.models import TenantDetails

app = typer.Typer(name="tenant", help="The DataLens instance.", no_args_is_help=True)


@app.command("details-get")
def details_get(*, datalens: DataLensClient) -> TenantDetails:
    """Print the DataLens instance the credentials reach (a safe auth probe)."""
    return datalens.tenant.details_get()
