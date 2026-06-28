"""TDD for WikiClient composition root — sub-clients share one session."""
import responses
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.pages.client import PagesClient
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.attachments.client import AttachmentsClient


def test_composes_subclients_over_shared_authed_session():
    client = WikiClient(oauth_token="tok", organization_id="org")
    assert isinstance(client.pages, PagesClient)
    assert isinstance(client.comments, CommentsClient)
    assert isinstance(client.attachments, AttachmentsClient)
    for sub in (client.pages, client.comments, client.attachments, client.me):
        assert sub._session.headers["Authorization"] == "OAuth tok"
        assert sub._session.headers["X-Org-Id"] == "org"


@responses.activate
def test_wiki_deps_factory_builds_from_env(monkeypatch):
    """_deps.wiki_client() reads env and returns a working WikiClient."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    from ycli.yandex.wiki._deps import wiki_client
    responses.add(responses.GET, "https://api.wiki.yandex.net/v1/users/me",
                  json={"username": "alice", "home_cluster": "homepage", "identity": {"uid": "1", "cloud_uid": "c1"}, "org": {"dir_id": "d1", "collab_id": "11111111-1111-1111-1111-111111111111"}},
                  status=200)
    client = wiki_client()
    assert isinstance(client, WikiClient)
    result = client.me.get()
    assert result.username == "alice"
