"""TDD for the Tracker external-applications client."""

import requests
import responses

from ycli.yandex.tracker.applications.client import ApplicationsClient
from ycli.yandex.tracker.applications.models import ApplicationList

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_applications_list():
    responses.add(
        responses.GET,
        f"{BASE}/applications",
        json=[{"id": "my-application", "type": "my-application", "name": "Application name"}],
        status=200,
    )
    out = ApplicationsClient(session=_session()).list()
    assert isinstance(out, ApplicationList) and out.root[0].id == "my-application"
    assert out.root[0].name == "Application name"
