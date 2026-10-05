"""DataLens FastMCP subserver — mounts the per-resource tool servers."""

from fastmcp import FastMCP

from ycli.yandex.datalens.mcp.resources import mcp as mcp_resources_mcp
from ycli.yandex.datalens.tenant.mcp import mcp as tenant_mcp

mcp = FastMCP(
    "datalens",
    instructions=(
        "Yandex DataLens. tenant_details_get tells which DataLens instance the credentials "
        "reach. DataLens needs a Yandex Cloud IAM token and a Yandex Cloud organization."
    ),
)
mcp.mount(tenant_mcp)
mcp.mount(mcp_resources_mcp)
