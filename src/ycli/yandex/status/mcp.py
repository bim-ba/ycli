"""Status FastMCP tool (read-only) — one auth probe per registered service."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.mcp import RO, EnvAuthSource, app_config
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter

mcp = FastMCP("status")
TAGS: set[str] = {"status"}


@mcp.tool(name="get", annotations={**RO, "title": "Check Yandex 360 auth status"}, tags=TAGS)
def get(config: AppConfig = Depends(app_config)) -> AuthReport:
    """Probe each service's identity endpoint; report which credentials work and whose they are.

    ``organization_id`` is left blank here — each service's account already identifies the
    authenticated user; the CLI ``auth status`` carries the org id.
    """
    reporter = StatusReporter.for_credentials(EnvAuthSource().resolve(), config)
    return reporter.report(configured=True, organization_id="")
