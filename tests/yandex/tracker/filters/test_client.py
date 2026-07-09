"""TDD for the Tracker filters client (get)."""

import requests
import responses

from ycli.yandex.tracker.filters.client import FiltersClient
from ycli.yandex.tracker.filters.models import Filter

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_filters_get():
    responses.add(
        responses.GET,
        f"{BASE}/filters/12345",
        json={
            "id": 12345,
            "name": "My open issues",
            "filter": {"assignee": "me()", "status": "open"},
            "favorite": False,
        },
        status=200,
    )
    out = FiltersClient(session=_session()).get(filter_id="12345")
    assert isinstance(out, Filter) and out.id == 12345
    assert out.filter == {"assignee": "me()", "status": "open"}
