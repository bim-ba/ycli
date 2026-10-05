"""DomainClient: one core session per domain client, closed with it; no empty credential."""

from http import HTTPMethod

import httpx2
import pytest
from pydantic import SecretStr

from tests.hosts import WIKI_BASE
from tests.mock_api import MockAPI
from ycli.yandex.core.auth import IAMTokenAuth
from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.cursor import WIKI_CURSOR


def test_an_empty_organization_is_refused_before_any_request():
    with pytest.raises(ValueError, match="an organization id is required"):
        TrackerClient(oauth_token="t", organization_id="")


@pytest.mark.parametrize(
    "credential", [{}, {"oauth_token": ""}, {"oauth_token": "t", "auth": httpx2.Auth()}]
)
def test_exactly_one_way_to_sign_in_is_required(credential):
    with pytest.raises(ValueError, match="one of the two"):
        TrackerClient(organization_id="o", **credential)


def test_any_auth_signs_the_requests_in_place_of_the_oauth_token():
    api = MockAPI()
    api.add("GET", "https://api.tracker.yandex.net/v3/myself", json={"login": "ivan"})
    auth = IAMTokenAuth(SecretStr("t1.secret"))
    with TrackerClient(auth=auth, organization_id="o", transport=api.transport()) as client:
        client.me.get()
    assert api.calls[0].headers["Authorization"] == "Bearer t1.secret"


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


def test_a_client_sends_any_endpoint_through_its_session(api):
    api.add("GET", f"{WIKI_BASE}/x", json={"results": [1]})
    with WikiClient(oauth_token="t", organization_id="o") as client:
        assert client.send(Endpoint(HTTPMethod.GET, "x", dict)) == {"results": [1]}


def test_a_client_walks_any_listing_through_its_session(api):
    api.add("GET", f"{WIKI_BASE}/x", json={"results": [1, 2], "next_cursor": "c"})
    api.add("GET", f"{WIKI_BASE}/x", json={"results": [3]})
    paged = Paged(Endpoint(HTTPMethod.GET, "x", dict), WIKI_CURSOR, lambda page: page["results"])
    with WikiClient(oauth_token="t", organization_id="o") as client:
        assert list(client.iterate(paged, limit=3)) == [1, 2, 3]
