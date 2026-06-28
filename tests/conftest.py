import pytest

from ycli.yandex.forms import _deps as forms_deps
from ycli.yandex.tracker import _deps as tracker_deps
from ycli.yandex.wiki import _deps as wiki_deps


@pytest.fixture(autouse=True)
def _reset_mcp_client_caches():
    """Each test builds its domain client fresh from its own env (the @cache is process-wide)."""
    tracker_deps.tracker_client.cache_clear()
    wiki_deps.wiki_client.cache_clear()
    forms_deps.forms_client.cache_clear()
    yield
