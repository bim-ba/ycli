"""DomainClient: one core session per domain client, closed with it; no empty credential."""

import pytest

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient


@pytest.mark.parametrize(("token", "organization"), [("", "o"), ("t", "")])
def test_an_empty_credential_is_refused_before_any_request(token, organization):
    with pytest.raises(ValueError, match="both required"):
        TrackerClient(oauth_token=token, organization_id=organization)


def test_leaving_the_with_block_closes_the_session():
    with TrackerClient(oauth_token="t", organization_id="o") as client:
        core = client.issues._session._client
        assert not core.is_closed
        assert client.queues._session is client.issues._session
    assert core.is_closed


@pytest.mark.parametrize(
    ("client_class", "url"),
    [
        (TrackerClient, "https://api.tracker.yandex.net/v3/myself"),
        (WikiClient, "https://api.wiki.yandex.net/v1/users/me"),
        (FormsClient, "https://api.forms.yandex.net/v1/users/me"),
    ],
)
def test_a_probe_is_one_read_of_the_services_own_me_endpoint(api, client_class, url):
    api.add("GET", url, json={})
    with client_class(oauth_token="t", organization_id="o") as client:
        client.probe()
    assert [str(call.url) for call in api.calls] == [url]
