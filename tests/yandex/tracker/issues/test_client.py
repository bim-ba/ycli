"""IssuesClient on the httpx2 core — wire shape of each operation, served by MockAPI."""

import pytest
from pydantic import SecretStr

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.session import connect
from ycli.yandex.tracker import SERVICE
from ycli.yandex.tracker.issues.client import IssuesClient
from ycli.yandex.tracker.issues.models import Issue, IssueList


def _client(api) -> IssuesClient:
    session = connect(
        SERVICE.profile,
        auth=OAuthTokenAuth(SecretStr("t")),
        organization_id="o",
        transport=api.transport(),
    )
    return IssuesClient(session=session)


def test_get_deserializes_issue(api):
    api.add(
        "GET",
        f"{BASE}/issues/DE-1",
        json={"key": "DE-1", "summary": "S", "type": {"key": "task"}},
        status=200,
    )
    i = _client(api).get("DE-1")
    assert isinstance(i, Issue)
    assert i.key == "DE-1" and i.type == "task"


def test_search_returns_issuelist(api):
    api.add(
        "POST",
        f"{BASE}/issues/_search",
        json=[{"key": "DE-1"}, {"key": "DE-2"}],
        status=200,
    )
    out = _client(api).search(body={"filter": {"queue": "DE"}})
    assert isinstance(out, IssueList)
    assert [i.key for i in out.root] == ["DE-1", "DE-2"]
    assert api.body(0) == {"filter": {"queue": "DE"}}


def test_count_returns_int(api):
    api.add("POST", f"{BASE}/issues/_count", json=7, status=200)
    assert _client(api).count(body={"filter": {"queue": "DE"}}) == 7


def test_create_posts_body(api):
    api.add("POST", f"{BASE}/issues/", json={"key": "DE-10", "summary": "New"}, status=201)
    i = _client(api).create(body={"queue": "DE", "summary": "New"})
    assert i.key == "DE-10"
    assert api.body(0) == {"queue": "DE", "summary": "New"}


def test_update_patches_body(api):
    api.add(
        "PATCH",
        f"{BASE}/issues/DE-5",
        json={"key": "DE-5", "summary": "Updated"},
        status=200,
    )
    i = _client(api).update("DE-5", body={"summary": "Updated"})
    assert i.summary == "Updated"
    assert api.calls[0].method == "PATCH"


def test_move_posts_with_queue_query(api):
    api.add("POST", f"{BASE}/issues/TEST-1/_move", json={"key": "NEW-1"}, status=200)
    i = _client(api).move("TEST-1", "NEW")
    assert isinstance(i, Issue) and i.key == "NEW-1"
    assert api.calls[0].method == "POST"
    assert "queue=NEW" in str(api.calls[0].url)


def test_suggest_passes_input_query(api):
    api.add("GET", f"{BASE}/issues/_suggest", json=[{"key": "TEST-123"}], status=200)
    out = _client(api).suggest("fix bug")
    assert isinstance(out, IssueList)
    assert out.root[0].key == "TEST-123"
    assert "input=fix" in str(api.calls[0].url)


def test_scroll_clear_posts_body_returns_none(api):
    api.add("POST", f"{BASE}/system/search/scroll/_clear", status=200)
    assert _client(api).scroll_clear({"scrollId": "scrollToken"}) is None
    assert api.calls[0].method == "POST"
    assert api.body(0) == {"scrollId": "scrollToken"}


def _page(start: int, count: int) -> list[dict]:
    return [{"key": f"DE-{n}"} for n in range(start, start + count)]


def test_search_walks_every_page(api):
    """#93: search used to return only Tracker's first page (50 issues) without a word."""
    api.add("POST", f"{BASE}/issues/_search", json=_page(1, 100), headers={"X-Total-Pages": "2"})
    api.add("POST", f"{BASE}/issues/_search", json=_page(101, 20), headers={"X-Total-Pages": "2"})
    out = _client(api).search({"query": "Queue: DE"})
    assert len(out.root) == 120
    assert [call.url.params["page"] for call in api.calls] == ["1", "2"]
    assert {call.url.params["perPage"] for call in api.calls} == {"100"}
    assert api.body(1) == {"query": "Queue: DE"}  # the body is re-sent with every page


def test_search_stops_at_the_limit_and_warns(api, caplog):
    api.add("POST", f"{BASE}/issues/_search", json=_page(1, 100), headers={"X-Total-Pages": "5"})
    out = _client(api).search({"query": "Queue: DE"}, limit=30)
    assert len(out.root) == 30
    assert len(api.calls) == 1
    assert api.calls[0].url.params["perPage"] == "30"  # no bigger page than the cap needs
    assert "stopped at 30 items; more may be available" in caplog.text


def test_search_without_more_pages_does_not_warn(api, caplog):
    api.add("POST", f"{BASE}/issues/_search", json=_page(1, 3), headers={"X-Total-Pages": "1"})
    out = _client(api).search({"query": "Queue: DE"}, limit=3)
    assert len(out.root) == 3
    assert "stopped at" not in caplog.text


def test_a_key_cannot_reach_another_endpoint(api):
    api.add("GET", f"{BASE}/issues/..%2Fqueues%2FDE", json={"key": "X"})
    _client(api).get("../queues/DE")
    assert api.calls[0].url.raw_path == b"/v3/issues/..%2Fqueues%2FDE"


def test_search_rejects_a_non_positive_limit(api):
    with pytest.raises(ValueError, match="positive"):
        _client(api).search({"query": "q"}, limit=0)
