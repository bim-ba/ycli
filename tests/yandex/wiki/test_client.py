"""TDD for WikiClient composition root — sub-clients share one session."""
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


def test_from_env_builds_authed_root(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    client = WikiClient.from_env()
    assert client.pages._session.headers["Authorization"] == "OAuth tok"
    assert client.pages._session.headers["X-Org-Id"] == "org"
