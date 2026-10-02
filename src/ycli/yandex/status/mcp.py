"""Status FastMCP tool (read-only) — whose token it is, its organization, one probe per service."""

from fastmcp import FastMCP
from fastmcp.dependencies import Depends

from ycli.settings import AppConfig
from ycli.yandex.mcp import RO, EnvAuthSource, app_config
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import build_report

mcp = FastMCP("status")
TAGS: set[str] = {"status"}


@mcp.tool(name="get", annotations={**RO, "title": "Check Yandex 360 auth status"}, tags=TAGS)
def get(config: AppConfig = Depends(app_config)) -> AuthReport:
    """Report whose token this is, its organization and which services accept it.

    ``identity`` is the token's owner (Yandex ID). ``organization`` is the configured id and, when
    the token has the ``directory:read_organization`` scope (API 360), its name. ``services`` has
    one probe each, with ``valid`` and, on failure, ``detail``.
    """
    return build_report(EnvAuthSource().resolve(), config)
