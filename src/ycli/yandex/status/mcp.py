"""Status FastMCP tool (read-only) — aggregate auth probe across all three services."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import ClientFactory
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.mcp import RO
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient

mcp = FastMCP("status")
TAGS: set[str] = {"status"}


@mcp.tool(name="get", annotations={**RO, "title": "Check Yandex 360 auth status"}, tags=TAGS)
def get(
    credentials: Credentials = Depends(Credentials),
    config: AppConfig = Depends(AppConfig),
) -> AuthReport:
    """Probe each service's identity endpoint; report which credentials work.

    ``organization_id`` is left blank here — the per-service ``me`` already identifies the
    authenticated user; the CLI ``auth status`` carries the org id.
    """
    tracker = ClientFactory.build(TrackerClient, credentials, config)
    me_clients = {"tracker": tracker.me}
    if not credentials.uses_service_account_iam:
        wiki = ClientFactory.build(WikiClient, credentials, config)
        forms = ClientFactory.build(FormsClient, credentials, config)
        me_clients.update({"wiki": wiki.me, "forms": forms.me})
    return StatusReporter(me_clients).report(configured=True, organization_id="")
