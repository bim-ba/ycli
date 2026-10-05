"""Yandex DataLens CLI — mounts the per-resource sub-apps."""

import typer

from ycli.yandex.datalens import SERVICE
from ycli.yandex.datalens.tenant.cli import app as tenant_app
from ycli.yandex.status.service_cli import service_auth_app

# Help text lives in the service registry (ycli.yandex.datalens.SERVICE).
app = typer.Typer(name="datalens", no_args_is_help=True)

app.add_typer(service_auth_app(SERVICE))
app.add_typer(tenant_app)
