"""Status FastMCP tool (read-only) — whose token it is, its organization, one probe per service."""

from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.mcp import ALWAYS_LOAD, RO, app_config, caller_credentials, new_server
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import build_report

mcp = new_server("status")


@mcp.tool(
    name="get",
    annotations={**RO, "title": "Check Yandex 360 auth status"},
    meta=ALWAYS_LOAD,
)
def get(config: AppConfig = Depends(app_config)) -> AuthReport:
    """Report whose token this is, its organization and which services accept it.

    ``credential`` says which token is in use (``oauth`` or ``iam``), never its value.
    ``identity`` is the token's owner (Yandex ID; unknown for an IAM token). ``organization`` is
    the configured id and, when the token has the ``directory:read_organization`` scope
    (API 360), its name. ``services`` has one probe each, with ``valid`` and, on failure,
    ``detail``.
    """
    return build_report(caller_credentials(), config)
