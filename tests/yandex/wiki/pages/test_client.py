"""TDD for PagesClient — pure declarative endpoints, mocked with `responses`."""

import json

import requests
import responses

from ycli.yandex.polling import poll
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.operations.client import OperationsClient
from ycli.yandex.wiki.pages.client import PagesClient
from ycli.yandex.wiki.pages.models import (
    GridRefList,
    PageCloneOperation,
    PageDeleteResult,
    PageDetails,
    PageRefList,
)

BASE = "https://api.wiki.yandex.net/v1"


def _client() -> PagesClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return PagesClient(session=s)


@responses.activate
def test_get_deserializes_pagedetails():
    responses.add(
        responses.GET,
        f"{BASE}/pages",
        json={"id": 1, "slug": "data/x", "title": "T", "content": "# B"},
        status=200,
    )
    page = _client().get(slug="data/x", fields="content")
    assert isinstance(page, PageDetails)
    assert page.content == "# B"
    assert responses.calls[0].request.params["slug"] == "data/x"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_descendants_single_page_no_cursor():
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 1, "slug": "data/a"}], "next_cursor": None},
        status=200,
    )
    out = _client().descendants(slug="data")
    assert isinstance(out, PageRefList)
    assert [r.slug for r in out.root] == ["data/a"]
    assert responses.calls[0].request.params["page_size"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_descendants_auto_drains_cursor(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 1, "slug": "a"}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 2, "slug": "b"}], "next_cursor": None},
        status=200,
    )
    client = WikiClient(oauth_token="t", organization_id="o")
    out = client.pages.descendants(slug="root")
    assert [r.slug for r in out.root] == ["a", "b"]


@responses.activate
def test_create_posts_body():
    responses.add(
        responses.POST, f"{BASE}/pages", json={"id": 7, "slug": "data/x", "title": "T"}, status=200
    )
    out = _client().create(body={"slug": "data/x", "title": "T", "content": "b"})
    assert out.id == 7
    assert json.loads(responses.calls[0].request.body)["slug"] == "data/x"  # ty: ignore[invalid-argument-type]


@responses.activate
def test_update_posts_to_pages_id():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42",
        json={"id": 42, "slug": "data/x", "title": "T"},
        status=200,
    )
    out = _client().update(page_id=42, body={"content": "b"})
    assert out.id == 42
    assert responses.calls[0].request.url.endswith("/pages/42")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_get_omits_fields_when_none():
    responses.add(
        responses.GET, f"{BASE}/pages", json={"id": 1, "slug": "s", "title": "t"}, status=200
    )
    _client().get(slug="s")
    assert "fields" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]


@responses.activate
def test_get_by_id_deserializes_pagedetails():
    responses.add(
        responses.GET,
        f"{BASE}/pages/12345",
        json={"id": 12345, "slug": "data/x", "title": "T", "content": "# B"},
        status=200,
    )
    page = _client().get_by_id(page_id=12345, fields="content")
    assert isinstance(page, PageDetails)
    assert page.id == 12345 and page.content == "# B"
    assert responses.calls[0].request.params["fields"] == "content"  # ty: ignore[unresolved-attribute]
    assert responses.calls[0].request.url.split("?")[0].endswith("/pages/12345")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_descendants_by_id_auto_drains_cursor():
    responses.add(
        responses.GET,
        f"{BASE}/pages/99/descendants",
        json={"results": [{"id": 1, "slug": "a"}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/99/descendants",
        json={"results": [{"id": 2, "slug": "b"}], "next_cursor": None},
        status=200,
    )
    out = _client().descendants_by_id(page_id=99)
    assert isinstance(out, PageRefList)
    assert [r.slug for r in out.root] == ["a", "b"]
    assert len(responses.calls) == 2
    assert responses.calls[1].request.params["cursor"] == "c1"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_grids_single_page_no_cursor():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/grids",
        json={"results": [{"id": "g-uuid", "title": "Roadmap"}], "next_cursor": None},
        status=200,
    )
    out = _client().grids(page_id=42)
    assert isinstance(out, GridRefList)
    assert [g.title for g in out.root] == ["Roadmap"]
    assert responses.calls[0].request.params["page_size"] == "50"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_grids_auto_drains_cursor_and_passes_order_by():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/grids",
        json={"results": [{"id": "g1", "title": "A"}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/grids",
        json={"results": [{"id": "g2", "title": "B"}], "next_cursor": None},
        status=200,
    )
    out = _client().grids(page_id=42, order_by="title")
    assert [g.id for g in out.root] == ["g1", "g2"]
    assert len(responses.calls) == 2
    assert responses.calls[0].request.params["order_by"] == "title"  # ty: ignore[unresolved-attribute]
    assert responses.calls[1].request.params["cursor"] == "c1"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_grids_limit_truncates_without_second_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/grids",
        json={"results": [{"id": "g1"}, {"id": "g2"}], "next_cursor": "c1"},
        status=200,
    )
    out = _client().grids(page_id=42, limit=1)
    assert [g.id for g in out.root] == ["g1"]
    assert len(responses.calls) == 1


@responses.activate
def test_delete_returns_recovery_token():
    responses.add(
        responses.DELETE,
        f"{BASE}/pages/42",
        json={"recovery_token": "a1b2-uuid"},
        status=200,
    )
    out = _client().delete(page_id=42)
    assert isinstance(out, PageDeleteResult)
    assert out.recovery_token == "a1b2-uuid"
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url.endswith("/pages/42")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_append_content_posts_body_and_returns_page():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/append-content",
        json={"id": 42, "slug": "data/x", "title": "T"},
        status=200,
    )
    out = _client().append_content(
        page_id=42, body={"content": "## More", "body": {"location": "bottom"}}
    )
    assert isinstance(out, PageDetails)
    assert out.id == 42
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url.endswith("/pages/42/append-content")  # ty: ignore[unresolved-attribute]
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"content": "## More", "body": {"location": "bottom"}}


@responses.activate
def test_clone_posts_body_and_returns_operation():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/clone",
        json={"operation": {"type": "clone", "id": "task-1"}, "status_url": "u"},
        status=200,
    )
    out = _client().clone(page_id=42, body={"target": "data/y", "subscribe_me": True})
    assert isinstance(out, PageCloneOperation)
    assert out.operation is not None and out.operation.id == "task-1"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url.endswith("/pages/42/clone")  # ty: ignore[unresolved-attribute]
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "target": "data/y",
        "subscribe_me": True,
    }


@responses.activate
def test_clone_wait_polls_operations_until_terminal():
    """The ``--wait`` path: after ``pages.clone`` triggers, poll() re-reads the clone operation.

    A scheduled → success status sequence with a recorder ``sleep`` (no real waiting): the loop
    fetches twice, sleeps exactly once in between, and returns the terminal status naming the copy.
    """
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    operations = OperationsClient(session=session)
    responses.add(
        responses.GET, f"{BASE}/operations/clone/task-1", json={"status": "scheduled"}, status=200
    )
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone/task-1",
        json={"status": "success", "result": {"page": {"id": 99, "slug": "data/y"}}},
        status=200,
    )
    slept: list[float] = []
    final = poll(
        lambda: operations.clone_get("task-1"),
        lambda state: state.is_terminal,
        sleep=slept.append,
    )
    assert final.status == "success"
    assert final.result is not None and final.result.page is not None
    assert final.result.page.slug == "data/y"
    assert len(responses.calls) == 2
    assert slept == [0.5]
