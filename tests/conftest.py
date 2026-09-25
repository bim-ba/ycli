import pytest

from ycli.yandex import mcp
from ycli.yandex.forms import dependencies as forms_deps
from ycli.yandex.tracker import dependencies as tracker_deps
from ycli.yandex.wiki import dependencies as wiki_deps


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    """Shared Yandex 360 credentials for every test.

    autouse so tests that never request it explicitly (registration-only / annotation-only
    tests) still get valid env, matching the ~47 files that previously relied on a local
    autouse fixture. Tests that need NO credentials always delete these env vars themselves
    (in their own body, or a file-local autouse fixture that runs after this one, since
    conftest.py autouse fixtures execute before module-level ones of the same scope) — which
    correctly overrides this fixture regardless of the values it pre-set.
    """
    for name in (
        "YANDEX_CLOUD_IAM_TOKEN",
        "YANDEX_CLOUD_ORGANIZATION_ID",
        "YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_ID",
        "YANDEX_CLOUD_SERVICE_ACCOUNT_ID",
        "YANDEX_CLOUD_SERVICE_ACCOUNT_PRIVATE_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@pytest.fixture(autouse=True)
async def _reset_mcp_client_caches():
    """Each test builds its domain client fresh from its own env (the @cache is process-wide)."""
    from ycli.mcp.server import mcp as root_mcp

    previous_auth = root_mcp.auth
    previous_lifespan = root_mcp._lifespan
    previous_request_auth = mcp.get_request_auth()
    root_mcp.auth = None
    mcp.set_request_auth(None)
    await mcp.reset_validation_cache()
    mcp.app_config.cache_clear()
    tracker_deps.tracker_client.cache_clear()
    wiki_deps.wiki_client.cache_clear()
    forms_deps.forms_client.cache_clear()
    yield
    root_mcp.auth = previous_auth
    root_mcp._lifespan = previous_lifespan
    mcp.set_request_auth(previous_request_auth)
    await mcp.reset_validation_cache()


@pytest.fixture(autouse=True)
async def _close_test_userinfo_client():
    """Close every test-installed pooled client, including mock replacements."""
    yield
    await mcp.close_userinfo_client()


@pytest.fixture
def loguru_sink():
    """Capture loguru output so token-secrecy assertions are provably non-vacuous."""
    import io

    from loguru import logger

    stream = io.StringIO()
    sink_id = logger.add(stream, level="DEBUG", backtrace=False, diagnose=False)
    try:
        yield stream
    finally:
        logger.remove(sink_id)
