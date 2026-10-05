"""DataLens FastMCP subserver — mounts the per-resource tool servers."""

from fastmcp import FastMCP

from ycli.yandex.datalens.collections.mcp import mcp as collections_mcp
from ycli.yandex.datalens.mcp.resources import mcp as mcp_resources_mcp
from ycli.yandex.datalens.tenant.mcp import mcp as tenant_mcp
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
mcp.mount(mcp_resources_mcp)
