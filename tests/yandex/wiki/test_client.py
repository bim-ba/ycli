"""TDD for WikiClient composition root — sub-clients share one session."""
import requests
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.pages.client import PagesClient
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.attachments.client import AttachmentsClient


def test_composes_subclients_over_one_session():
    s = requests.Session()
    c = WikiClient(session=s)
    assert isinstance(c.pages, PagesClient)
    assert isinstance(c.comments, CommentsClient)
    assert isinstance(c.attachments, AttachmentsClient)
    # all sub-clients share the injected session
    assert c.pages._session is s and c.comments._session is s and c.attachments._session is s


def test_from_env_builds_authed_root(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    c = WikiClient.from_env()
    assert c.pages._session.headers["Authorization"] == "OAuth tok"
    assert c.pages._session.headers["X-Org-Id"] == "org"
