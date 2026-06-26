"""TDD for MeClient — pure declarative endpoint, mocked with `responses`."""
import requests
import responses

from ycli.yandex.forms.me.client import MeClient
from ycli.yandex.forms.me.models import User

BASE = "https://api.forms.yandex.net/v1"


def _client() -> MeClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return MeClient(session=s)


@responses.activate
def test_get_returns_user_model():
    responses.add(responses.GET, f"{BASE}/users/me",
                  json={"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"}, status=200)
    u = _client().get()
    assert isinstance(u, User)
    assert u.email == "e@x"
    assert responses.calls[0].request.url == f"{BASE}/users/me"
