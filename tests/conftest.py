import pytest

from ycli.yandex import mcp
from ycli.yandex.forms import dependencies as forms_deps
from ycli.yandex.tracker import dependencies as tracker_deps
from ycli.yandex.wiki import dependencies as wiki_deps


@pytest.fixture(autouse=True)
def _reset_mcp_client_caches():
    """Each test builds its domain client fresh from its own env (the @cache is process-wide)."""
    mcp.app_config.cache_clear()
    tracker_deps.tracker_client.cache_clear()
    wiki_deps.wiki_client.cache_clear()
    forms_deps.forms_client.cache_clear()
    yield
