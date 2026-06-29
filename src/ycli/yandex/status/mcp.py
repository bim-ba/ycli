"""Status FastMCP tool (read-only) — aggregate auth probe across all three services."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.yandex._mcp import RO
from ycli.yandex.forms._deps import forms_client
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter
from ycli.yandex.tracker._deps import tracker_client
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki._deps import wiki_client
from ycli.yandex.wiki.client import WikiClient

mcp = FastMCP("status")
TAGS: set[str] = {"status"}


@mcp.tool(name="get", annotations={**RO, "title": "Check Yandex 360 auth status"}, tags=TAGS)
def get(
    tracker: TrackerClient = Depends(tracker_client),
    wiki: WikiClient = Depends(wiki_client),
    forms: FormsClient = Depends(forms_client),
) -> AuthReport:
    """Probe each service's identity endpoint; report which credentials work.

    ``organization_id`` is left blank here — the per-service ``me`` already identifies the
    authenticated user; the CLI ``auth status`` carries the org id.
    """
    me_clients = {"tracker": tracker.me, "wiki": wiki.me, "forms": forms.me}
    return StatusReporter(me_clients).report(configured=True, organization_id="")
