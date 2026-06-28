"""FastMCP dependency provider for the forms subserver — one cached client per process.

fastmcp v3 isolates each mounted server's lifespan, so the canonical way to share a single
non-serializable client across mounted tools is a module-level cached factory (see the
fastmcp composition docs). ``@cache`` builds the client once from the env on first tool call;
tests reset it via the autouse ``cache_clear`` fixture in tests/conftest.py.
"""

from functools import cache

from ycli.settings import AppConfig, Credentials
from ycli.yandex._mcp import RO as RO
from ycli.yandex.forms.client import FormsClient

TAGS: set[str] = {"forms"}


@cache
def forms_client() -> FormsClient:
    """Build (once) and return the forms client from the environment."""
    credentials, config = Credentials(), AppConfig()  # ty: ignore[missing-argument]
    return FormsClient(
        oauth_token=credentials.oauth_token,
        organization_id=credentials.organization_id,
        timeout_seconds=int(config.timeout_seconds),
        retries=config.retries,
    )
