"""DataLens tenant FastMCP tool (read-only) — Depends DI, native error handling."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import RO, datalens_client
from ycli.yandex.datalens.tenant.models import TenantDetails

mcp = FastMCP("datalens-tenant")


@mcp.tool(name="tenant_details_get", annotations={**RO, "title": "Get the DataLens instance"})
def details_get(client: DataLensClient = Depends(datalens_client)) -> TenantDetails:
    """The DataLens instance the credentials reach (a safe auth probe)."""
    return client.tenant.details_get()
