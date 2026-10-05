"""Each pagination kind: the first request it shapes and the next one it derives."""

import json

import httpx2
import pytest

from ycli.yandex.core.pagination import (
    BodyCursorPagination,
    CursorPagination,
    LinkHeaderPagination,
    NextURLPagination,
    OffsetLimitPagination,
    PageNumberPagination,
    RelativeIDPagination,
    ScrollPagination,
)

BASE = "https://api.test/v1/items"


def _request(url: str = BASE) -> httpx2.Request:
    return httpx2.Request("POST", url, json={"filter": {}}, headers={"X-Org-Id": "o"})


def test_offset_limit():
    pagination = OffsetLimitPagination(page_size=2)
    first = pagination.first(_request())
    assert dict(first.url.params) == {"offset": "0", "limit": "2"}
    second = pagination.next(first, httpx2.Response(200), [1, 2])
    assert second is not None
    assert second.url.params["offset"] == "2"
    assert second.content == first.content  # body and headers travel with every page
    assert second.headers["X-Org-Id"] == "o"
    assert pagination.next(second, httpx2.Response(200), [3]) is None  # a short page ends it


def test_page_number_stops_at_total_pages_or_a_short_page():
    pagination = PageNumberPagination(page_size=2)
    first = pagination.first(_request())
    assert dict(first.url.params) == {"page": "1", "perPage": "2"}
    full = httpx2.Response(200, headers={"X-Total-Pages": "2"})
    second = pagination.next(first, full, [1, 2])
    assert second is not None
    assert second.url.params["page"] == "2"
    assert pagination.next(second, full, [3, 4]) is None  # page 2 of 2
    assert pagination.next(first, httpx2.Response(200), [1]) is None  # short page, no header


def test_page_number_trusts_the_total_over_a_capped_page():
    """A server that caps perPage below page_size sends short pages that are not the last."""
    pagination = PageNumberPagination(page_size=100)
    first = pagination.first(_request())
    capped = httpx2.Response(200, headers={"X-Total-Pages": "3"})
    following = pagination.next(first, capped, list(range(50)))
    assert following is not None
    assert following.url.params["page"] == "2"


def test_page_number_without_the_total_header():
    pagination = PageNumberPagination(page_size=1, total_pages_header=None)
    first = pagination.first(_request())
    assert pagination.next(first, httpx2.Response(200), [1]) is not None


def test_cursor_from_the_body_and_a_non_advancing_cursor():
    pagination = CursorPagination(cursor_of=lambda response: response.json()["next_cursor"])
    first = pagination.first(_request())
    second = pagination.next(first, httpx2.Response(200, json={"next_cursor": "c2"}), [1])
    assert second is not None
    assert second.url.params["cursor"] == "c2"
    assert pagination.next(second, httpx2.Response(200, json={"next_cursor": "c2"}), [2]) is None
    assert pagination.next(second, httpx2.Response(200, json={"next_cursor": None}), [2]) is None


def test_a_body_cursor_goes_into_the_json_body_and_keeps_the_rest_of_it():
    pagination = BodyCursorPagination(
        cursor_of=lambda response: response.json().get("nextPageToken"), page_size=50
    )
    first = pagination.first(_request())
    assert json.loads(first.content) == {"filter": {}, "pageSize": 50}
    second = pagination.next(first, httpx2.Response(200, json={"nextPageToken": "t2"}), [1])
    assert second is not None
    assert json.loads(second.content) == {"filter": {}, "pageSize": 50, "pageToken": "t2"}
    # The request is otherwise the same: method, address, headers, and a length for the new body.
    assert (second.method, second.url, second.headers["X-Org-Id"]) == ("POST", first.url, "o")
    assert second.headers["Content-Length"] == str(len(second.content))
    assert pagination.next(second, httpx2.Response(200, json={"nextPageToken": "t2"}), [2]) is None
    assert pagination.next(second, httpx2.Response(200, json={}), [2]) is None


def test_a_body_cursor_works_without_a_page_size_and_without_a_body():
    """DataLens names the cursor ``page`` in four listings; a call with no arguments has no body."""
    pagination = BodyCursorPagination(
        cursor_of=lambda response: response.json()["nextPageToken"], cursor_param="page"
    )
    bare = httpx2.Request("POST", BASE)
    assert pagination.first(bare) is bare
    following = pagination.next(bare, httpx2.Response(200, json={"nextPageToken": "2"}), [1])
    assert following is not None
    assert json.loads(following.content) == {"page": "2"}


def test_link_header_copies_only_the_query_of_a_schemeless_link():
    pagination = LinkHeaderPagination()
    link = '<api.tracker.yandex.net/v3/issues/_search?id=abc&perPage=10>; rel="next"'
    following = pagination.next(_request(), httpx2.Response(200, headers={"Link": link}), [1])
    assert following is not None
    assert str(following.url) == f"{BASE}?id=abc&perPage=10"
    assert pagination.next(_request(), httpx2.Response(200), [1]) is None


def test_next_url_follows_the_body_link_and_stops_on_repeat():
    pagination = NextURLPagination(url_of=lambda response: response.json().get("next"))
    following = pagination.next(
        _request(), httpx2.Response(200, json={"next": f"{BASE}?page=2"}), [1]
    )
    assert following is not None
    assert str(following.url) == f"{BASE}?page=2"
    assert (
        pagination.next(following, httpx2.Response(200, json={"next": f"{BASE}?page=2"}), [1])
        is None
    )
    assert pagination.next(following, httpx2.Response(200, json={}), [1]) is None


def test_next_url_can_carry_only_the_query_of_a_dead_link():
    """Forms prints answers links under a retired /v3/ route: keep the path, take the cursor."""
    pagination = NextURLPagination(
        url_of=lambda response: response.json().get("next"), query_only=True
    )
    response = httpx2.Response(200, json={"next": "/v3/surveys/S1/answers/?id=100"})
    following = pagination.next(_request(), response, [1])
    assert following is not None
    assert str(following.url) == f"{BASE}?id=100"
    assert pagination.next(following, response, [1]) is None


def test_scroll_follows_the_header_and_stops_without_it_or_without_items():
    pagination = ScrollPagination()
    named = httpx2.Response(200, headers={"X-Scroll-Id": "scr-1"})
    following = pagination.next(_request(f"{BASE}?scrollType=sorted"), named, [1, 2])
    assert following is not None
    assert dict(following.url.params) == {"scrollType": "sorted", "scrollId": "scr-1"}
    assert pagination.next(following, httpx2.Response(200), [3]) is None
    assert pagination.next(following, named, []) is None


@pytest.mark.parametrize("items", [[], [{"id": None}]])
def test_relative_id_stops_without_a_last_id(items):
    pagination = RelativeIDPagination(id_of=lambda item: item["id"])
    assert pagination.next(_request(), httpx2.Response(200), items) is None


def test_relative_id_advances_and_stops_on_repeat():
    pagination = RelativeIDPagination(id_of=lambda item: item["id"])
    following = pagination.next(_request(), httpx2.Response(200), [{"id": "1"}, {"id": "9"}])
    assert following is not None
    assert following.url.params["id"] == "9"
    assert pagination.next(following, httpx2.Response(200), [{"id": "9"}]) is None


def test_a_next_page_on_another_host_gets_its_own_host_header():
    pagination = NextURLPagination(url_of=lambda response: response.json()["next"])
    response = httpx2.Response(200, json={"next": "https://cdn.test/v1/items?page=2"})
    following = pagination.next(_request(), response, [1])
    assert following is not None
    assert following.headers["Host"] == "cdn.test"


def test_a_body_cursor_is_sent_as_the_number_it_is_read_as():
    """DataLens takes the page of two listings by its number, and page 0 is a page."""
    pagination = BodyCursorPagination(
        cursor_of=lambda response: response.json().get("page"), cursor_param="page"
    )
    bare = httpx2.Request("POST", BASE)
    first = pagination.next(bare, httpx2.Response(200, json={"page": 0}), [1])
    assert first is not None
    assert json.loads(first.content) == {"page": 0}
    assert pagination.next(first, httpx2.Response(200, json={"page": 0}), [1]) is None
    assert pagination.next(first, httpx2.Response(200, json={"page": ""}), [1]) is None
    assert pagination.next(first, httpx2.Response(200, json={}), [1]) is None
