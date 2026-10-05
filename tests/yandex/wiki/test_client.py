"""WikiClient wires every resource to one httpx2 core session."""

from tests.hosts import WIKI_BASE as BASE
from ycli.yandex.core.resource import Resource
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.dependencies import wiki_client


def test_every_resource_shares_one_core_session():
    with WikiClient(oauth_token="t", organization_id="o") as client:
        resources = [value for value in vars(client).values() if isinstance(value, Resource)]
        assert len(resources) == 10
        assert len({id(resource._session) for resource in resources}) == 1


def test_the_mcp_provider_builds_a_client_from_the_environment(api):
    api.add("GET", f"{BASE}/users/me", json={"username": "alice"})
    with wiki_client() as client:
        assert client.me.get().username == "alice"
    assert api.calls[0].headers["Authorization"] == "OAuth t"
    assert api.calls[0].headers["X-Org-Id"] == "o"
