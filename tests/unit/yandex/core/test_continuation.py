"""A listing taken in pieces is the listing taken whole, for every way a service pages."""

import asyncio
import base64
import json
from collections.abc import Callable
from http import HTTPMethod

import httpx2
import pytest
from pydantic import SecretStr

from ycli.cli.errors import exit_code_for
from ycli.cli.exit_codes import ExitCode
from ycli.settings import HTTPConfig
from ycli.yandex.core import continuation
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Effect, Endpoint, Paged
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
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect, connect_async
from ycli.yandex.errors import (
    YandexAuthError,
    YandexInvalidRequestError,
    YandexStaleContinuationError,
)

BASE = "https://api.test/v1"
DATA = list(range(1, 12))  # eleven items, three to a page: the last page is short
PAGE = 3
type Handler = Callable[[httpx2.Request], httpx2.Response]


def _page(start: int) -> list[int]:
    return DATA[start : start + PAGE]


def _offset(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(200, json=_page(int(request.url.params.get("offset", 0))))


def _numbered(request: httpx2.Request) -> httpx2.Response:
    start = (int(request.url.params.get("page", 1)) - 1) * PAGE
    headers = {"X-Total-Pages": "4", "X-Total-Count": str(len(DATA))}
    return httpx2.Response(200, json=_page(start), headers=headers)


def _cursor(request: httpx2.Request) -> httpx2.Response:
    cursor = request.url.params.get("cursor", "c0")
    if not cursor.startswith("c"):
        return httpx2.Response(400, json={"error_code": "BAD_REQUEST"})
    start = int(cursor[1:])
    following = f"c{start + PAGE}" if start + PAGE < len(DATA) else None
    return httpx2.Response(200, json={"items": _page(start), "next": following})


def _in_body(request: httpx2.Request) -> httpx2.Response:
    start = int(json.loads(request.content).get("pageToken", 0))
    following = start + PAGE if start + PAGE < len(DATA) else None
    return httpx2.Response(200, json={"items": _page(start), "nextPageToken": following})


def _linked(request: httpx2.Request) -> httpx2.Response:
    page = int(request.url.params.get("page", 1))
    more = page * PAGE < len(DATA)
    # As Tracker prints it: with no scheme, and with the query of the next page.
    link = {"Link": f'<api.test/v1/items?page={page + 1}>; rel="next"'} if more else {}
    return httpx2.Response(200, json=_page((page - 1) * PAGE), headers=link)


def _next_url(request: httpx2.Request) -> httpx2.Response:
    start = int(request.url.params.get("after", 0))
    more = start + PAGE < len(DATA)
    link = f"{BASE}/retired/items?after={start + PAGE}" if more else None
    return httpx2.Response(200, json={"items": _page(start), "next_url": link})


def _after_id(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(200, json=_page(int(request.url.params.get("id", 0))))


class Scroll:
    """A scroll as Tracker keeps it: the place is the server's, and moves with every request."""

    def __init__(self) -> None:
        self.places: dict[str, int] = {}

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        scroll = request.url.params.get("scrollId")
        if scroll is None:
            scroll = f"s{len(self.places)}"
            self.places[scroll] = 0
        elif scroll not in self.places:
            return httpx2.Response(403, json={"errorMessages": ["Некорректная подпись."]})
        start = self.places[scroll]
        self.places[scroll] = start + PAGE
        return httpx2.Response(200, json=_page(start), headers={"X-Scroll-Id": scroll})


def _items(page: dict) -> list[int]:
    return page["items"]


def _get(kind: type = list[int]) -> Endpoint:
    return Endpoint(HTTPMethod.GET, "items", kind)


WAYS: dict[str, tuple[Handler | type, Paged]] = {
    "offset": (_offset, Paged(_get(), OffsetLimitPagination(page_size=PAGE), list)),
    "page number": (_numbered, Paged(_get(), PageNumberPagination(page_size=PAGE), list)),
    "cursor": (_cursor, Paged(_get(dict), CursorPagination(lambda r: r.json()["next"]), _items)),
    "cursor in the body": (
        _in_body,
        Paged(
            Endpoint(HTTPMethod.POST, "items", dict, json={"scope": "all"}, effect=Effect.READ),
            BodyCursorPagination(lambda r: r.json()["nextPageToken"]),
            _items,
        ),
    ),
    "link header": (_linked, Paged(_get(), LinkHeaderPagination(), list)),
    "next url": (
        _next_url,
        Paged(
            _get(dict), NextURLPagination(lambda r: r.json()["next_url"], query_only=True), _items
        ),
    ),
    "relative id": (_after_id, Paged(_get(), RelativeIDPagination(id_of=str), list)),
    "scroll": (Scroll, Paged(_get(), ScrollPagination(), list)),
}


def _served(way: str) -> tuple[httpx2.MockTransport, Paged]:
    serve, paged = WAYS[way]
    handler = serve() if isinstance(serve, type) else serve
    return httpx2.MockTransport(handler), paged


def _connect(transport: httpx2.MockTransport, factory=connect):
    return factory(
        ServiceProfile(BASE),
        auth=OAuthTokenAuth(SecretStr("y0_secret")),
        organization_id="org",
        http=HTTPConfig(retries=1),
        transport=transport,
    )


def _token(paged: Paged, first: httpx2.Request, url: httpx2.URL) -> str:
    """A token of ``paged`` that names the page at ``url``, as the walk would write it."""
    page = httpx2.Request(first.method, url, content=first.content)
    way = type(paged.pagination).__name__
    return continuation.encode(first, page, way=way, skip=0, seen=0)


def _in_pieces(way: str, limit: int) -> list[list[int]]:
    """The listing taken ``limit`` at a time, each call going on from the token of the last."""
    transport, paged = _served(way)
    session = _connect(transport)
    pieces, token = [], None
    for _ in range(len(DATA) + 2):
        got = session.iterate(paged, limit=limit, next=token).collect()
        pieces.append(got.items)
        if not got.truncated:
            assert got.next is None
            return pieces
        token = got.next
    raise AssertionError(f"the listing never ended: {pieces}")


@pytest.mark.parametrize("way", sorted(WAYS))
def test_a_listing_with_no_limit_is_whole_and_says_it_ended(way):
    transport, paged = _served(way)
    got = _connect(transport).iterate(paged).collect()
    assert (got.items, got.truncated, got.next) == (DATA, False, None)


@pytest.mark.parametrize("limit", range(1, len(DATA) + 2))
@pytest.mark.parametrize("way", sorted(set(WAYS) - {"scroll"}))
def test_pieces_of_a_listing_are_the_listing_whatever_the_limit_cuts(way, limit):
    """Between two pages or in the middle of one: nothing twice, nothing lost, ``limit`` each."""
    pieces = _in_pieces(way, limit)
    assert [item for piece in pieces for item in piece] == DATA
    assert all(len(piece) == limit for piece in pieces[:-1])


@pytest.mark.parametrize("limit", range(1, len(DATA) + 2))
def test_a_scroll_is_cut_only_between_pages_and_loses_nothing(limit):
    """The server moves its place with every request, so a page that was asked is given whole."""
    pieces = _in_pieces("scroll", limit)
    assert [item for piece in pieces for item in piece] == DATA
    # A scroll learns that it ended only by asking once more: the last call may give nothing.
    assert all(pieces[:-1]), "a call that is not the last gives at least one page"
    if limit >= PAGE:
        # Whole pages, as many as fit: never more than was asked for.
        assert all(len(piece) <= limit for piece in pieces)
        assert all(len(piece) % PAGE == 0 for piece in pieces if piece[-1:] != DATA[-1:])


def test_a_token_of_a_scroll_works_once():
    transport, paged = _served("scroll")
    session = _connect(transport)
    token = session.iterate(paged, limit=PAGE).collect().next
    assert token is not None
    assert session.iterate(paged, limit=PAGE, next=token).collect().items == [4, 5, 6]
    # The same token again goes on from where the server now stands, not from the same place.
    assert session.iterate(paged, limit=PAGE, next=token).collect().items == [7, 8, 9]


def test_a_token_of_a_page_that_can_be_asked_again_works_any_number_of_times():
    transport, paged = _served("cursor")
    session = _connect(transport)
    token = session.iterate(paged, limit=4).collect().next
    again = [session.iterate(paged, limit=4, next=token).collect().items for _ in range(2)]
    assert again == [[5, 6, 7, 8], [5, 6, 7, 8]]


def test_the_total_is_given_where_the_service_says_it():
    transport, paged = _served("page number")
    got = _connect(transport).iterate(paged, limit=2).collect()
    assert (got.total, got.truncated) == (len(DATA), True)
    transport, paged = _served("cursor")
    assert _connect(transport).iterate(paged, limit=2).collect().total is None


def test_a_listing_is_lazy_and_knows_where_it_stopped_once_it_was_read():
    asked = []

    def counted(request: httpx2.Request) -> httpx2.Response:
        asked.append(request)
        return _cursor(request)

    listing = _connect(httpx2.MockTransport(counted)).iterate(WAYS["cursor"][1], limit=4)
    assert asked == [] and listing.next is None
    assert next(listing) == 1 and len(asked) == 1
    assert list(listing) == [2, 3, 4] and len(asked) == 2
    assert listing.truncated and listing.next and listing.total is None


def test_a_token_goes_on_only_the_listing_that_gave_it():
    transport, paged = _served("cursor")
    session = _connect(transport)
    token = session.iterate(paged, limit=4).collect().next
    # Another operation, or the same one on another object: another path.
    other = Paged(Endpoint(HTTPMethod.GET, "queues", dict), paged.pagination, _items)
    with pytest.raises(YandexInvalidRequestError, match="is of another listing"):
        session.iterate(other, limit=4, next=token)
    posted = Paged(Endpoint(HTTPMethod.POST, "items", dict), paged.pagination, _items)
    with pytest.raises(YandexInvalidRequestError, match="is of another listing"):
        session.iterate(posted, limit=4, next=token)


def test_the_other_arguments_of_the_call_that_goes_on_take_no_part():
    """The token carries the query and the body of its page: a filter given anew changes nothing."""
    transport, paged = _served("cursor")
    session = _connect(transport)
    token = session.iterate(paged, limit=4).collect().next
    filtered = Paged(
        Endpoint(HTTPMethod.GET, "items", dict, params={"q": "b"}), paged.pagination, _items
    )
    assert session.iterate(filtered, limit=4, next=token).collect().items == [5, 6, 7, 8]


def _packed(state: str) -> str:
    return base64.urlsafe_b64encode(state.encode()).decode()


@pytest.mark.parametrize(
    "garbage",
    [
        "",
        "not-a-token",
        "e30",  # an empty object
        _packed(
            '{"v":2,"of":"","query":"","way":"CursorPagination","body":"","skip":0,"seen":0}'
        ),  # another version
        _packed('{"v":1,"of":"","query":"","way":"CursorPagination","body":"","skip":-1,"seen":0}'),
        _packed(
            '{"v":1,"of":"","query":"","way":"CursorPagination","body":"","skip":"0","seen":0}'
        ),  # text where a number goes
        # A key a token does not have: it cannot name a path, nor anything else.
        _packed(
            '{"v":1,"of":"","query":"","way":"CursorPagination","body":"","skip":0,"seen":0,"path":"/v1/other"}'
        ),
    ],
)
def test_what_is_not_a_token_is_refused_before_anything_is_sent(garbage):
    transport, paged = _served("cursor")
    session = _connect(transport)
    with pytest.raises(YandexInvalidRequestError, match="is not a token a listing gave"):
        session.iterate(paged, next=garbage)


def test_a_token_too_long_to_be_one_is_not_read(monkeypatch):
    """What a caller far away sends is bounded before it is decoded."""
    transport, paged = _served("cursor")
    session = _connect(transport)
    read = []
    monkeypatch.setattr(
        continuation.Continuation,
        "model_validate_json",
        classmethod(lambda cls, data: read.append(data)),
    )
    with pytest.raises(YandexInvalidRequestError, match="is not a token a listing gave"):
        session.iterate(
            paged, next="A" * (HTTPConfig().max_token_length + 4)
        )  # well-formed base64, only too long
    assert read == []


def test_a_token_carries_no_path_and_no_other_version():
    first = httpx2.Request("GET", f"{BASE}/items")
    elsewhere = httpx2.Request("GET", f"{BASE}/queues?page=2")
    with pytest.raises(YandexInvalidRequestError, match="at another path than its listing"):
        continuation.encode(first, elsewhere, way="PageNumberPagination", skip=0, seen=0)
    page = httpx2.Request("GET", f"{BASE}/items?page=2")
    token = continuation.encode(first, page, way="PageNumberPagination", skip=1, seen=4)
    resumed, state = continuation.resume(first, token, way="PageNumberPagination", longest=1000)
    assert (str(resumed.url), state.skip, state.seen) == (f"{BASE}/items?page=2", 1, 4)
    assert continuation.way_of(token, longest=1000) == "PageNumberPagination"
    assert len(token) < 190 and token.isascii() and "=" not in token


@pytest.mark.parametrize(
    ("way", "dead"),
    [("cursor", "x9"), ("scroll", "s404")],
)
def test_a_continuation_the_service_no_longer_takes_says_start_again(way, dead):
    """Each way of paging knows how its service refuses: 400 for a cursor, 403 for a scroll."""
    transport, paged = _served(way)
    session = _connect(transport)
    first = paged.pagination.first(paged.endpoint.request(session._client))
    param = "cursor" if way == "cursor" else "scrollId"
    stale = _token(paged, first, first.url.copy_merge_params({param: dead}))
    with pytest.raises(YandexStaleContinuationError, match="start it again without it") as caught:
        session.iterate(paged, next=stale).collect()
    assert exit_code_for(caught.value) is ExitCode.STALE
    assert isinstance(caught.value.__cause__, Exception)


def test_a_refusal_of_a_listing_that_was_not_continued_stays_what_it_is():
    def refused(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(403, json={"errorMessages": ["no access"]})

    session = _connect(httpx2.MockTransport(refused))
    with pytest.raises(YandexAuthError):
        session.iterate(WAYS["scroll"][1]).collect()


def test_an_asynchronous_session_pages_the_same_way():
    async def pieces() -> list[list[int]]:
        transport, paged = _served("cursor")
        session = _connect(transport, connect_async)
        found, token = [], None
        while True:
            listing = session.iterate(paged, limit=4, next=token)
            first = await anext(listing)
            got = await listing.collect()
            found.append([first, *got.items])
            if not got.truncated:
                assert (listing.next, listing.total, listing.seen) == (None, None, len(DATA))
                assert session.way_of(token) == "CursorPagination"
                return found
            token = listing.next

    assert asyncio.run(pieces()) == [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11]]


def test_an_asynchronous_session_says_start_again_too():
    async def continued() -> None:
        transport, paged = _served("cursor")
        session = _connect(transport, connect_async)
        first = paged.pagination.first(paged.endpoint.request(session._client))
        dead = httpx2.Request("GET", first.url.copy_merge_params({"cursor": "x9"}))
        token = _token(paged, first, dead.url)
        await session.iterate(paged, next=token).collect()

    with pytest.raises(YandexStaleContinuationError):
        asyncio.run(continued())


def _narrowed(limit: int | None) -> Paged:
    """A listing whose client narrows the page to the limit, as ``tracker.boards.list`` does."""
    size = min(PAGE, limit) if limit else PAGE
    return Paged(
        Endpoint(HTTPMethod.GET, "items", list[int], params={"perPage": size}),
        RelativeIDPagination(id_of=str),
        list,
    )


def test_a_token_goes_on_with_another_limit_though_the_limit_shapes_the_page():
    """The token carries its listing: of the call that goes on, only the limit counts."""

    def served(request: httpx2.Request) -> httpx2.Response:
        start = int(request.url.params.get("id", 0))
        return httpx2.Response(200, json=DATA[start : start + int(request.url.params["perPage"])])

    session = _connect(httpx2.MockTransport(served))
    first = session.iterate(_narrowed(2), limit=2).collect()
    assert first.items == [1, 2] and first.next
    # Another limit builds another first request (`perPage=3`): the token still goes on.
    rest = session.iterate(_narrowed(3), limit=3, next=first.next).collect()
    assert rest.items == [3, 4, 5]
    assert session.iterate(_narrowed(None), next=rest.next).collect().items == DATA[5:]


def test_a_token_of_another_way_of_paging_the_same_path_is_of_another_listing():
    """A search by pages and the same search by a scroll share a method and a path."""
    transport, by_scroll = _served("scroll")
    session = _connect(transport)
    token = session.iterate(by_scroll, limit=PAGE).collect().next
    assert token and session.way_of(token) == "ScrollPagination"
    by_pages = Paged(_get(), PageNumberPagination(page_size=PAGE), list)
    with pytest.raises(YandexInvalidRequestError, match="is of another listing"):
        session.iterate(by_pages, limit=PAGE, next=token)


@pytest.mark.parametrize("way", sorted(WAYS))
def test_a_token_whose_state_its_way_cannot_read_is_refused_and_never_a_traceback(way):
    """Right in form and of the right way, and naming a request the way cannot go on from."""
    transport, paged = _served(way)
    session = _connect(transport)
    first = paged.pagination.first(paged.endpoint.request(session._client))
    # No state at all: the query the way writes its place into is gone.
    bare = _token(paged, first, first.url.copy_with(query=b""))
    try:
        got = session.iterate(paged, limit=PAGE, next=bare).collect()
    except (YandexInvalidRequestError, YandexStaleContinuationError):
        return  # refused as a token, by ycli or by the service
    assert got.items == DATA[:PAGE]  # or read as the start of the listing: nothing else


def test_a_listing_whose_total_was_given_whole_is_not_truncated():
    """Two boards and a limit of two: the service says there are two, so nothing is left."""

    def served(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=[1, 2], headers={"X-Total-Count": "2"})

    session = _connect(httpx2.MockTransport(served))
    paged = Paged(_get(), RelativeIDPagination(id_of=str), list)
    got = session.iterate(paged, limit=2).collect()
    assert (got.items, got.truncated, got.next, got.total) == ([1, 2], False, None, 2)


def test_the_total_ends_a_listing_taken_in_pieces_too():
    """What the calls before gave is in the token, so the last piece knows it is the last."""
    transport, paged = _served("page number")  # eleven items, and the service says so
    session = _connect(transport)
    first = session.iterate(paged, limit=6).collect()
    assert first.truncated and first.next
    listing = session.iterate(paged, limit=5, next=first.next)
    rest = listing.collect()
    assert (rest.items, rest.truncated, rest.next) == (DATA[6:], False, None)
    # A listing counts what it and the calls before it gave: eleven, not the five of this one.
    assert listing.seen == len(DATA)


def test_a_way_that_fails_on_a_listing_nobody_continued_fails_as_itself():
    """Only a token is blamed for a state that cannot be read; a defect of a way stays one."""

    class Broken(RelativeIDPagination):
        def next(self, request, response, items):
            raise KeyError("page")

    session = _connect(httpx2.MockTransport(_after_id))
    with pytest.raises(KeyError):
        session.iterate(Paged(_get(), Broken(id_of=str), list)).collect()
