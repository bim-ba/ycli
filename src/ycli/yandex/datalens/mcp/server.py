"""DataLens FastMCP subserver — mounts the per-resource tool servers.

The server of one resource (``…<resource>.mcp.mcp``) is a building block: whoever mounts one
in a server of their own adds ``ArgumentRefusals`` to it, or a refusal of arguments repeats
what was sent. This server carries it.
"""

from fastmcp import FastMCP

from ycli.yandex.datalens.audit.mcp import mcp as audit_mcp
from ycli.yandex.datalens.charts.mcp import mcp as charts_mcp
from ycli.yandex.datalens.cloudenvironments.mcp import mcp as cloudenvironments_mcp
from ycli.yandex.datalens.cloudenvironmentstorage.mcp import mcp as cloudenvironmentstorage_mcp
from ycli.yandex.datalens.collections.mcp import mcp as collections_mcp
from ycli.yandex.datalens.connections.mcp import mcp as connections_mcp
from ycli.yandex.datalens.dashboards.mcp import mcp as dashboards_mcp
from ycli.yandex.datalens.datasets.mcp import mcp as datasets_mcp
from ycli.yandex.datalens.embeddingsecrets.mcp import mcp as embeddingsecrets_mcp
from ycli.yandex.datalens.embeds.mcp import mcp as embeds_mcp
from ycli.yandex.datalens.entries.mcp import mcp as entries_mcp
from ycli.yandex.datalens.entrylocks.mcp import mcp as entrylocks_mcp
from ycli.yandex.datalens.htmlpages.mcp import mcp as htmlpages_mcp
from ycli.yandex.datalens.lakehouseoperations.mcp import mcp as lakehouseoperations_mcp
from ycli.yandex.datalens.licensing.mcp import mcp as licensing_mcp
from ycli.yandex.datalens.mcp.resources import mcp as mcp_resources_mcp
from ycli.yandex.datalens.members.mcp import mcp as members_mcp
from ycli.yandex.datalens.permissions.mcp import mcp as permissions_mcp
from ycli.yandex.datalens.reports.mcp import mcp as reports_mcp
from ycli.yandex.datalens.restcatalogs.mcp import mcp as restcatalogs_mcp
from ycli.yandex.datalens.sharedentries.mcp import mcp as sharedentries_mcp
from ycli.yandex.datalens.sparkapplications.mcp import mcp as sparkapplications_mcp
from ycli.yandex.datalens.sparkclusters.mcp import mcp as sparkclusters_mcp
from ycli.yandex.datalens.sqlqueries.mcp import mcp as sqlqueries_mcp
from ycli.yandex.datalens.tenant.mcp import mcp as tenant_mcp
from ycli.yandex.datalens.trinoclusters.mcp import mcp as trinoclusters_mcp
from ycli.yandex.datalens.workbookexports.mcp import mcp as workbookexports_mcp
from ycli.yandex.datalens.workbookimports.mcp import mcp as workbookimports_mcp
from ycli.yandex.datalens.workbooks.mcp import mcp as workbooks_mcp
from ycli.yandex.mcp import ArgumentRefusals

mcp = FastMCP(
    "datalens",
    instructions=(
        "Yandex DataLens. tenant_details_get tells which DataLens instance the credentials "
        "reach. DataLens needs a Yandex Cloud IAM token and a Yandex Cloud organization."
    ),
)
# The root server carries it too; this one for whoever mounts the service alone.
mcp.add_middleware(ArgumentRefusals())
mcp.mount(tenant_mcp)
mcp.mount(collections_mcp)
mcp.mount(workbooks_mcp)
mcp.mount(entrylocks_mcp)
mcp.mount(sparkclusters_mcp)
mcp.mount(htmlpages_mcp)
mcp.mount(members_mcp)
mcp.mount(entries_mcp)
mcp.mount(permissions_mcp)
mcp.mount(connections_mcp)
mcp.mount(datasets_mcp)
mcp.mount(charts_mcp)
mcp.mount(dashboards_mcp)
mcp.mount(reports_mcp)
mcp.mount(workbookexports_mcp)
mcp.mount(workbookimports_mcp)
mcp.mount(embeds_mcp)
mcp.mount(embeddingsecrets_mcp)
mcp.mount(sharedentries_mcp)
mcp.mount(audit_mcp)
mcp.mount(sqlqueries_mcp)
mcp.mount(licensing_mcp)
mcp.mount(cloudenvironments_mcp)
mcp.mount(cloudenvironmentstorage_mcp)
mcp.mount(restcatalogs_mcp)
mcp.mount(lakehouseoperations_mcp)
mcp.mount(trinoclusters_mcp)
mcp.mount(sparkapplications_mcp)
mcp.mount(mcp_resources_mcp)
