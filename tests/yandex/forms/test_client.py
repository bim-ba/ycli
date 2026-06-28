"""TDD for FormsClient composition root — sub-clients share one session."""
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.me.client import MeClient


def test_composes_subclients_over_shared_authed_session():
    client = FormsClient(oauth_token="tok", organization_id="org")
    assert isinstance(client.me, MeClient)
    for sub in (client.me, client.surveys, client.questions, client.answers):
        assert sub._session.headers["Authorization"] == "OAuth tok"
        assert sub._session.headers["X-Org-Id"] == "org"


def test_from_env_builds_authed_root(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    client = FormsClient.from_env()
    assert client.me._session.headers["Authorization"] == "OAuth tok"
    assert client.me._session.headers["X-Org-Id"] == "org"
