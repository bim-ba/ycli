"""DataLens FastMCP subserver — mounts the per-resource tool servers."""

from fastmcp import FastMCP

from ycli.yandex.datalens.audit.mcp import mcp as audit_mcp
from ycli.yandex.datalens.charts.mcp import mcp as charts_mcp
from ycli.yandex.datalens.collections.mcp import mcp as collections_mcp
from ycli.yandex.datalens.connections.mcp import mcp as connections_mcp
from ycli.yandex.datalens.datasets.mcp import mcp as datasets_mcp
from ycli.yandex.datalens.embeddingsecrets.mcp import mcp as embeddingsecrets_mcp
from ycli.yandex.datalens.embeds.mcp import mcp as embeds_mcp
from ycli.yandex.datalens.entries.mcp import mcp as entries_mcp
from ycli.yandex.datalens.entrylocks.mcp import mcp as entrylocks_mcp
from ycli.yandex.datalens.mcp.resources import mcp as mcp_resources_mcp
from ycli.yandex.datalens.members.mcp import mcp as members_mcp
from ycli.yandex.datalens.permissions.mcp import mcp as permissions_mcp
from ycli.yandex.datalens.reports.mcp import mcp as reports_mcp
from ycli.yandex.datalens.sharedentries.mcp import mcp as sharedentries_mcp
from ycli.yandex.datalens.sqlqueries.mcp import mcp as sqlqueries_mcp
from ycli.yandex.datalens.tenant.mcp import mcp as tenant_mcp
from ycli.yandex.datalens.workbookexports.mcp import mcp as workbookexports_mcp
from ycli.yandex.datalens.workbookimports.mcp import mcp as workbookimports_mcp
from ycli.yandex.datalens.workbooks.mcp import mcp as workbooks_mcp

mcp = FastMCP(
    "datalens",
    instructions=(
        "Yandex DataLens. tenant_details_get tells which DataLens instance the credentials "
        "reach. DataLens needs a Yandex Cloud IAM token and a Yandex Cloud organization."
    ),
)
mcp.mount(tenant_mcp)
mcp.mount(collections_mcp)
mcp.mount(workbooks_mcp)
mcp.mount(entrylocks_mcp)
mcp.mount(members_mcp)
mcp.mount(entries_mcp)
mcp.mount(permissions_mcp)
mcp.mount(connections_mcp)
mcp.mount(datasets_mcp)
mcp.mount(charts_mcp)
mcp.mount(reports_mcp)
mcp.mount(workbookexports_mcp)
mcp.mount(workbookimports_mcp)
mcp.mount(embeds_mcp)
mcp.mount(embeddingsecrets_mcp)
mcp.mount(sharedentries_mcp)
mcp.mount(audit_mcp)
mcp.mount(sqlqueries_mcp)
mcp.mount(mcp_resources_mcp)
