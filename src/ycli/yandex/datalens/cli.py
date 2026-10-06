"""Yandex DataLens CLI — mounts the per-resource sub-apps."""

import typer

from ycli.yandex.datalens import SERVICE
from ycli.yandex.datalens.charts.cli import app as charts_app
from ycli.yandex.datalens.collections.cli import app as collections_app
from ycli.yandex.datalens.connections.cli import app as connections_app
from ycli.yandex.datalens.datasets.cli import app as datasets_app
from ycli.yandex.datalens.entries.cli import app as entries_app
from ycli.yandex.datalens.entrylocks.cli import app as entrylocks_app
from ycli.yandex.datalens.members.cli import app as members_app
from ycli.yandex.datalens.permissions.cli import app as permissions_app
from ycli.yandex.datalens.tenant.cli import app as tenant_app
from ycli.yandex.datalens.workbookexports.cli import app as workbookexports_app
from ycli.yandex.datalens.workbookimports.cli import app as workbookimports_app
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
app.add_typer(entries_app)
app.add_typer(permissions_app)
app.add_typer(connections_app)
app.add_typer(datasets_app)
app.add_typer(charts_app)
app.add_typer(workbookexports_app)
app.add_typer(workbookimports_app)
