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
def _reset_mcp_client_caches():
    """Each test builds its domain client fresh from its own env (the @cache is process-wide)."""
    mcp.app_config.cache_clear()
    tracker_deps.tracker_client.cache_clear()
    wiki_deps.wiki_client.cache_clear()
    forms_deps.forms_client.cache_clear()
    yield
