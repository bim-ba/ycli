"""TDD for the Tracker components client."""

import requests
import responses

from ycli.yandex.tracker.components.client import ComponentsClient
from ycli.yandex.tracker.components.models import ComponentList

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_components_list():
    responses.add(
        responses.GET,
        f"{BASE}/components",
        json=[
            {
                "id": 1,
                "name": "Test",
                "queue": {"key": "ORG", "display": "My queue"},
                "assignAuto": False,
            }
        ],
        status=200,
    )
    out = ComponentsClient(session=_session()).list()
    assert isinstance(out, ComponentList) and out.root[0].name == "Test"
    assert out.root[0].queue.key == "ORG" and out.root[0].assign_auto is False
