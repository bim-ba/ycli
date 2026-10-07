"""Yandex DataLens CLI — mounts the per-resource sub-apps."""

import typer

from ycli.yandex.datalens import SERVICE
from ycli.yandex.datalens.audit.cli import app as audit_app
from ycli.yandex.datalens.charts.cli import app as charts_app
from ycli.yandex.datalens.cloudenvironments.cli import app as cloudenvironments_app
from ycli.yandex.datalens.cloudenvironmentstorage.cli import app as cloudenvironmentstorage_app
from ycli.yandex.datalens.collections.cli import app as collections_app
from ycli.yandex.datalens.connections.cli import app as connections_app
from ycli.yandex.datalens.dashboards.cli import app as dashboards_app
from ycli.yandex.datalens.datasets.cli import app as datasets_app
from ycli.yandex.datalens.embeddingsecrets.cli import app as embeddingsecrets_app
from ycli.yandex.datalens.embeds.cli import app as embeds_app
from ycli.yandex.datalens.entries.cli import app as entries_app
from ycli.yandex.datalens.entrylocks.cli import app as entrylocks_app
from ycli.yandex.datalens.lakehouseoperations.cli import app as lakehouseoperations_app
from ycli.yandex.datalens.licensing.cli import app as licensing_app
from ycli.yandex.datalens.members.cli import app as members_app
from ycli.yandex.datalens.permissions.cli import app as permissions_app
from ycli.yandex.datalens.reports.cli import app as reports_app
from ycli.yandex.datalens.restcatalogs.cli import app as restcatalogs_app
from ycli.yandex.datalens.sharedentries.cli import app as sharedentries_app
from ycli.yandex.datalens.sparkapplications.cli import app as sparkapplications_app
from ycli.yandex.datalens.sqlqueries.cli import app as sqlqueries_app
from ycli.yandex.datalens.tenant.cli import app as tenant_app
from ycli.yandex.datalens.trinoclusters.cli import app as trinoclusters_app
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
app.add_typer(dashboards_app)
app.add_typer(reports_app)
app.add_typer(workbookexports_app)
app.add_typer(workbookimports_app)
app.add_typer(embeds_app)
app.add_typer(embeddingsecrets_app)
app.add_typer(sharedentries_app)
app.add_typer(audit_app)
app.add_typer(sqlqueries_app)
app.add_typer(licensing_app)
app.add_typer(cloudenvironments_app)
app.add_typer(cloudenvironmentstorage_app)
app.add_typer(restcatalogs_app)
app.add_typer(lakehouseoperations_app)
app.add_typer(trinoclusters_app)
app.add_typer(sparkapplications_app)
