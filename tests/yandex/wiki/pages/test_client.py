"""TDD for PagesClient — pure declarative endpoints, mocked with `responses`."""
import json
import requests
import responses
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.pages.client import PagesClient
from ycli.yandex.wiki.pages.models import PageDetails, PageRefList

BASE = "https://api.wiki.yandex.net/v1"


def _client() -> PagesClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return PagesClient(session=s)


@responses.activate
def test_get_deserializes_pagedetails():
    responses.add(responses.GET, f"{BASE}/pages",
                  json={"id": 1, "slug": "data/x", "title": "T", "content": "# B"}, status=200)
    page = _client().get(slug="data/x", fields="content")
    assert isinstance(page, PageDetails)
    assert page.content == "# B"
    assert responses.calls[0].request.params["slug"] == "data/x"


@responses.activate
def test_descendants_single_page_no_cursor():
    responses.add(responses.GET, f"{BASE}/pages/descendants",
                  json={"results": [{"id": 1, "slug": "data/a"}], "next_cursor": None}, status=200)
    out = _client().descendants(slug="data")
    assert isinstance(out, PageRefList)
    assert [r.slug for r in out.root] == ["data/a"]
    assert responses.calls[0].request.params["page_size"] == "100"


@responses.activate
def test_descendants_auto_drains_cursor(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(responses.GET, f"{BASE}/pages/descendants",
                  json={"results": [{"id": 1, "slug": "a"}], "next_cursor": "c1"}, status=200)
    responses.add(responses.GET, f"{BASE}/pages/descendants",
                  json={"results": [{"id": 2, "slug": "b"}], "next_cursor": None}, status=200)
    client = WikiClient(oauth_token="t", organization_id="o")
    out = client.pages.descendants(slug="root")
    assert [r.slug for r in out.root] == ["a", "b"]


@responses.activate
def test_create_posts_body():
    responses.add(responses.POST, f"{BASE}/pages",
                  json={"id": 7, "slug": "data/x", "title": "T"}, status=200)
    out = _client().create(body={"slug": "data/x", "title": "T", "content": "b"})
    assert out.id == 7
    assert json.loads(responses.calls[0].request.body)["slug"] == "data/x"


@responses.activate
def test_update_posts_to_pages_id():
    responses.add(responses.POST, f"{BASE}/pages/42",
                  json={"id": 42, "slug": "data/x", "title": "T"}, status=200)
    out = _client().update(page_id=42, body={"content": "b"})
    assert out.id == 42
    assert responses.calls[0].request.url.endswith("/pages/42")


@responses.activate
def test_get_omits_fields_when_none():
    responses.add(responses.GET, f"{BASE}/pages",
                  json={"id": 1, "slug": "s", "title": "t"}, status=200)
    _client().get(slug="s")
    assert "fields" not in responses.calls[0].request.params
