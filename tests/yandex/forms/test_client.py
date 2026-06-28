"""TDD for FormsClient composition root — sub-clients share one session."""

import responses
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.me.client import MeClient


def test_composes_subclients_over_shared_authed_session():
    client = FormsClient(oauth_token="tok", organization_id="org")
    assert isinstance(client.me, MeClient)
    for sub in (client.me, client.surveys, client.questions, client.answers):
        assert sub._session.headers["Authorization"] == "OAuth tok"
        assert sub._session.headers["X-Org-Id"] == "org"


@responses.activate
def test_forms_deps_factory_builds_from_env(monkeypatch):
    """_deps.forms_client() reads env and returns a working FormsClient."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    from ycli.yandex.forms._deps import forms_client

    responses.add(
        responses.GET,
        "https://api.forms.yandex.net/v1/users/me",
        json={"id": 1, "uid": "u", "cloud_uid": "c", "email": "e@x"},
        status=200,
    )
    client = forms_client()
    assert isinstance(client, FormsClient)
    result = client.me.get()
    assert result.email == "e@x"
