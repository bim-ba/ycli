"""FastMCP dependency provider for the wiki subserver — one cached client per process.

fastmcp v3 isolates each mounted server's lifespan, so the canonical way to share a single
non-serializable client across mounted tools is a module-level cached factory (see the
fastmcp composition docs). ``@cache`` builds the client once from the env on first tool call;
tests reset it via the autouse ``cache_clear`` fixture in tests/conftest.py.
"""

from functools import cache

from ycli.yandex._mcp import RO as RO
from ycli.yandex.settings import AppConfig, Credentials
from ycli.yandex.wiki.client import WikiClient

TAGS: set[str] = {"wiki"}


@cache
def wiki_client() -> WikiClient:
    """Build (once) and return the wiki client from the environment."""
    credentials, config = Credentials(), AppConfig()
    return WikiClient(
        oauth_token=credentials.oauth_token,
        organization_id=credentials.organization_id,
        timeout_seconds=int(config.timeout_seconds),
        retries=config.retries,
    )
