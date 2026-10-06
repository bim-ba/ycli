"""Yandex DataLens CLI — mounts the per-resource sub-apps."""

import typer

from ycli.yandex.datalens import SERVICE
from ycli.yandex.datalens.collections.cli import app as collections_app
from ycli.yandex.datalens.entrylocks.cli import app as entrylocks_app
from ycli.yandex.datalens.members.cli import app as members_app
from ycli.yandex.datalens.tenant.cli import app as tenant_app
from ycli.yandex.datalens.workbooks.cli import app as workbooks_app
from ycli.yandex.status.service_cli import service_auth_app

# Help text lives in the service registry (ycli.yandex.datalens.SERVICE).
app = typer.Typer(name="datalens", no_args_is_help=True)

app.add_typer(service_auth_app(SERVICE))
app.add_typer(tenant_app)
app.add_typer(collections_app)
app.add_typer(workbooks_app)
app.add_typer(entrylocks_app)
app.add_typer(members_app)
