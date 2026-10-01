"""Each pagination kind: the first request it shapes and the next one it derives."""

import httpx2
import pytest

from ycli.yandex.core.pagination import (
    CursorPagination,
    HeaderCursorPagination,
    LinkHeaderPagination,
    NextURLPagination,
    OffsetLimitPagination,
    PageNumberPagination,
    RelativeIdPagination,
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
    assert pagination.next(first, httpx2.Response(200), [1]) is None  # short page


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


def test_header_cursor_reads_the_scroll_id():
    pagination = HeaderCursorPagination()
    response = httpx2.Response(200, headers={"X-Scroll-Id": "s1"})
    following = pagination.next(_request(), response, [1])
    assert following is not None
    assert following.url.params["scrollId"] == "s1"


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


@pytest.mark.parametrize("items", [[], [{"id": None}]])
def test_relative_id_stops_without_a_last_id(items):
    pagination = RelativeIdPagination(id_of=lambda item: item["id"])
    assert pagination.next(_request(), httpx2.Response(200), items) is None


def test_relative_id_advances_and_stops_on_repeat():
    pagination = RelativeIdPagination(id_of=lambda item: item["id"])
    following = pagination.next(_request(), httpx2.Response(200), [{"id": "1"}, {"id": "9"}])
    assert following is not None
    assert following.url.params["id"] == "9"
    assert pagination.next(following, httpx2.Response(200), [{"id": "9"}]) is None
