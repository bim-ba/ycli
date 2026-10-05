"""Yandex DataLens domain — per-resource clients, CLI, and MCP over its RPC API."""

from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.service import Service

# The version of the API the generated models were written for. DataLens adds a version on a
# breaking change; the weekly api-drift run reports a new specification.
API_VERSION = "3"

SERVICE = Service(
    name="datalens",
    help="Yandex DataLens: workbooks, connections, datasets, charts, dashboards.",
    client="ycli.yandex.datalens.client:DataLensClient",
    cli="ycli.yandex.datalens.cli:app",
    mcp="ycli.yandex.datalens.mcp.server:mcp",
    profile=ServiceProfile(
        "https://api.datalens.tech",
        org_header=None,
        cloud_org_header="x-dl-org-id",
        headers={"x-dl-api-version": API_VERSION},
        oauth_token=False,
    ),
)
