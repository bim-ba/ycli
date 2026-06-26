"""TDD for FormsClient composition root — sub-clients share one session."""
import requests

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.me.client import MeClient


def test_composes_subclients_over_one_session():
    s = requests.Session()
    c = FormsClient(session=s)
    assert isinstance(c.me, MeClient)
    for sub in (c.me, c.surveys, c.questions, c.answers):
        assert sub._session is s


def test_from_env_builds_authed_root(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    c = FormsClient.from_env()
    assert c.me._session.headers["Authorization"] == "OAuth tok"
    assert c.me._session.headers["X-Org-Id"] == "org"
