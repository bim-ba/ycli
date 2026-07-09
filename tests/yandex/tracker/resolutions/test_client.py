"""TDD for ResolutionsClient — GET /resolutions."""

import requests
import responses

from ycli.yandex.tracker.resolutions.client import ResolutionsClient
from ycli.yandex.tracker.resolutions.models import ResolutionList

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_resolutions_list():
    responses.add(
        responses.GET,
        f"{BASE}/resolutions",
        json=[{"id": 1, "key": "fixed", "name": "Решен"}],
        status=200,
    )
    out = ResolutionsClient(session=_session()).list()
    assert isinstance(out, ResolutionList)
    assert out.root[0].key == "fixed" and out.root[0].name == "Решен"
