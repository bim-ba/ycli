"""TDD for StatusesClient — GET /statuses."""

import requests
import responses

from ycli.yandex.tracker.statuses.client import StatusesClient
from ycli.yandex.tracker.statuses.models import StatusList

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_statuses_list():
    responses.add(
        responses.GET,
        f"{BASE}/statuses",
        json=[{"id": 1, "key": "open", "name": "Открыт", "type": "new"}],
        status=200,
    )
    out = StatusesClient(session=_session()).list()
    assert isinstance(out, StatusList)
    assert out.root[0].key == "open" and out.root[0].type == "new"
