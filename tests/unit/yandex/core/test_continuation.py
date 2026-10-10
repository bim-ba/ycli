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
from ycli.yandex.core.endpoint import Effect, Endpoint, Paged, segment
from ycli.yandex.core.listing import Listing
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
    return continuation.encode(first, page, way=way, skip=0, seen=0, organization="X-Org-Id: org")


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
    assert asked == []
    assert next(listing) == 1 and len(asked) == 1
    assert list(listing) == [2, 3, 4] and len(asked) == 2
    assert listing.truncated and listing.next and listing.total is None


def test_a_token_goes_on_only_the_listing_that_gave_it():
    transport, paged = _served("cursor")
    session = _connect(transport)
    token = session.iterate(paged, limit=4).collect().next
    # Another operation, or the same one on another object: another path.
    other = Paged(Endpoint(HTTPMethod.GET, "queues", dict), paged.pagination, _items)
    named = r"it differs in the address: queues \(the token holds items\)$"
    with pytest.raises(YandexInvalidRequestError, match=named):
        session.iterate(other, limit=4, next=token)
    deeper = Paged(Endpoint(HTTPMethod.GET, "items/7/sub", dict), paged.pagination, _items)
    with pytest.raises(YandexInvalidRequestError, match="is of another listing than GET"):
        session.iterate(deeper, limit=4, next=token)
    posted = Paged(Endpoint(HTTPMethod.POST, "items", dict), paged.pagination, _items)
    with pytest.raises(YandexInvalidRequestError, match="is of another listing"):
        session.iterate(posted, limit=4, next=token)


def _asked(**params: str) -> Paged:
    """The listing of the cursor, as a call that gives ``params`` asks for it."""
    return Paged(
        Endpoint(HTTPMethod.GET, "items", dict, params=params), WAYS["cursor"][1].pagination, _items
    )


def test_an_argument_given_again_that_is_not_the_token_s_is_refused_by_its_name():
    """What a call that goes on gives has to be what its token holds: nothing is passed over."""
    transport, _ = _served("cursor")
    session = _connect(transport)
    token = session.iterate(_asked(q="a", kind="x"), limit=4).collect().next
    with pytest.raises(YandexInvalidRequestError, match=r"it differs in: q$"):
        session.iterate(_asked(q="b", kind="x"), limit=4, next=token)
    # What the first call did not give is not the token's either.
    with pytest.raises(YandexInvalidRequestError, match=r"it differs in: q, kind$"):
        session.iterate(
            _asked(q="b", kind="y"), limit=4, next=session.iterate(_asked(), limit=4).collect().next
        )


def test_what_is_given_again_as_it_was_goes_on_and_what_is_left_out_stays_the_token_s():
    transport, _ = _served("cursor")
    session = _connect(transport)
    token = session.iterate(_asked(q="a", kind="x"), limit=4).collect().next
    # All of it again, a part of it, or none: the page is the token's.
    for again in (_asked(q="a", kind="x"), _asked(q="a"), _asked()):
        assert session.iterate(again, limit=4, next=token).collect().items == [5, 6, 7, 8]


def _in_body_asked(body: object) -> Paged:
    endpoint = Endpoint(HTTPMethod.POST, "items", dict, json=body, effect=Effect.READ)
    return Paged(endpoint, WAYS["cursor in the body"][1].pagination, _items)


def test_a_body_given_again_is_held_key_by_key_and_nothing_is_in_anything():
    session = _connect(httpx2.MockTransport(_in_body))
    first = {"query": "a", "filter": {"queue": "DE", "tags": ["x"]}, "expand": None}
    token = session.iterate(_in_body_asked(first), limit=4).collect().next
    for again in (first, {"query": "a"}, {"filter": {}}, {"filter": {"queue": "DE"}}, {}):
        got = session.iterate(_in_body_asked(again), limit=4, next=token).collect()
        assert got.items == [5, 6, 7, 8], again
    for other, named in (
        ({"query": "b"}, "query"),
        ({"filter": {"queue": "QA"}}, "filter"),
        ({"filter": {"tags": ["x", "y"]}}, "filter"),
        ({"fields": "key"}, "fields"),
    ):
        with pytest.raises(YandexInvalidRequestError, match=rf"it differs in: {named}$"):
            session.iterate(_in_body_asked(other), limit=4, next=token)


def test_a_body_that_is_no_object_is_held_whole():
    session = _connect(httpx2.MockTransport(_in_body))
    paged = _in_body_asked({"query": "a"})
    token = session.iterate(paged, limit=4).collect().next
    with pytest.raises(YandexInvalidRequestError, match=r"it differs in: the body$"):
        session.iterate(_in_body_asked(["a"]), limit=4, next=token)
    first = paged.endpoint.request(httpx2.Client(base_url=BASE))
    bare = continuation.encode(first, first, way="BodyCursorPagination", skip=0, seen=0)
    listed = httpx2.Request("POST", f"{BASE}/items", json=["a"])
    held = continuation.encode(listed, listed, way="BodyCursorPagination", skip=0, seen=0)
    resume = continuation.resume
    assert resume(listed, listed, held, way="BodyCursorPagination", longest=1000)
    with pytest.raises(YandexInvalidRequestError, match=r"it differs in: the body$"):
        resume(listed, first, bare, way="BodyCursorPagination", longest=1000)


def test_a_token_whose_body_cannot_be_read_is_not_a_token():
    first = httpx2.Request("POST", f"{BASE}/items", json={"query": "a"})
    torn = httpx2.Request("POST", f"{BASE}/items", content=b"{")
    token = continuation.encode(first, torn, way="BodyCursorPagination", skip=0, seen=0)
    with pytest.raises(YandexInvalidRequestError, match="is not a token a listing gave"):
        continuation.resume(first, first, token, way="BodyCursorPagination", longest=1000)


def _written(**changed: object) -> str:
    """A token as the walk writes it, with ``changed`` written over it: one field gone wrong."""
    state: dict[str, object] = {"v": 2, "of": "", "at": "/v1/items", "org": "X-Org-Id: org"}
    state |= {"way": "CursorPagination", "query": "", "body": "", "skip": 0, "seen": 0}
    state |= {"kept": {}}
    return base64.urlsafe_b64encode(json.dumps(state | changed).encode()).decode()


@pytest.mark.parametrize(
    "garbage",
    [
        "",
        "not-a-token",
        "e30",  # an empty object
        "WzFd",  # a list
        _written(v=3),  # a version this one does not know
        _written(skip=-1),
        _written(skip="0"),  # text where a number goes
        _written(kept={"scrollToken": 1}),  # a number where text goes
        # A key a token does not have: it cannot name a host, nor anything else.
        _written(host="evil.example"),
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


def test_a_token_is_short_and_its_page_lies_at_the_path_of_its_listing():
    first = httpx2.Request("GET", f"{BASE}/items")
    elsewhere = httpx2.Request("GET", f"{BASE}/queues?page=2")
    with pytest.raises(YandexInvalidRequestError, match="at another path than its listing"):
        continuation.encode(first, elsewhere, way="PageNumberPagination", skip=0, seen=0)
    page = httpx2.Request("GET", f"{BASE}/items?page=2")
    token = continuation.encode(first, page, way="PageNumberPagination", skip=1, seen=4)
    resumed, state = continuation.resume(
        first, first, token, way="PageNumberPagination", longest=1000
    )
    assert (str(resumed.url), state.skip, state.seen) == (f"{BASE}/items?page=2", 1, 4)
    assert continuation.way_of(token, longest=1000) == "PageNumberPagination"
    assert len(token) < 240 and token.isascii() and "=" not in token


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
            with pytest.raises(RuntimeError, match="is not read to its end"):
                _ = listing.next  # not known before the listing is read, here as well
            got = await listing.collect()
            found.append([first, *got.items])
            if not got.truncated:
                assert (listing.next, listing.total, listing.seen) == (None, None, len(DATA))
                assert session.way_of(token) == "CursorPagination"
                assert session.kept_of(token) == {}
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
        Endpoint(HTTPMethod.GET, "items", list[int]),
        RelativeIDPagination(id_of=str, page_size=size),
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
    said = r"taken another way \(ScrollPagination, where this call takes it by PageNumberPag"
    with pytest.raises(YandexInvalidRequestError, match=said):
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


def test_a_link_of_the_service_that_names_another_page_size_still_goes_on():
    """The page size is the pager's, so the call that goes on gives none to differ (#559)."""

    def served(request: httpx2.Request) -> httpx2.Response:
        start = int(request.url.params.get("id", 0))
        size = int(request.url.params["page_size"])
        # The link narrows the page by itself, as a service may.
        link = f"/items/?survey=s1&page_size=2&id={start + size}"
        following = link if start + size < len(DATA) else None
        return httpx2.Response(200, json={"items": DATA[start : start + size], "next": following})

    def asked(**params: str) -> Paged:
        pager = NextURLPagination(lambda r: r.json()["next"], query_only=True, page_size=PAGE)
        return Paged(Endpoint(HTTPMethod.GET, "items", dict, params=params), pager, _items)

    session = _connect(httpx2.MockTransport(served))
    first = session.iterate(asked(survey="s1"), limit=4).collect()
    assert first.items == [1, 2, 3, 4]
    # The token holds the request of the link (`page_size=2`); the call gives only what is its.
    rest = session.iterate(asked(), limit=3, next=first.next).collect()
    assert rest.items == [5, 6, 7]
    assert session.iterate(asked(survey="s1"), next=rest.next).collect().items == DATA[7:]


def _unheaded(request: httpx2.Request) -> httpx2.Response:
    """Pages by number or by offset of the size the request asks, and no header of how many."""
    asked = request.url.params
    size = int(asked.get("perPage") or asked["limit"])
    start = (int(asked["page"]) - 1) * size if "page" in asked else int(asked["offset"])
    return httpx2.Response(200, json=DATA[start : start + size])


@pytest.mark.parametrize("pager", [PageNumberPagination, OffsetLimitPagination])
def test_a_listing_gone_on_ends_by_the_page_size_of_its_token_not_of_the_call(pager):
    """A short page is the last one by the size that was asked for, which is the token's (#534)."""

    def narrowed(limit: int | None) -> Paged:
        return Paged(_get(), pager(page_size=min(100, limit) if limit else 100), list)

    session = _connect(httpx2.MockTransport(_unheaded))
    first = session.iterate(narrowed(2), limit=2).collect()
    assert first.items == [1, 2] and first.next
    # The call that goes on would ask for pages of 100; the token asks for pages of 2.
    rest = session.iterate(narrowed(None), next=first.next).collect()
    assert (rest.items, rest.truncated, rest.next) == (DATA[2:], False, None)


def test_a_listing_stopped_by_the_cap_on_pages_says_so_and_goes_on(caplog):
    """What the cap on pages cut is not the end: it is truncated, with a token to go on from."""
    transport, paged = _served("offset")
    session = connect(
        ServiceProfile(BASE),
        auth=OAuthTokenAuth(SecretStr("y0_secret")),
        organization_id="org",
        http=HTTPConfig(retries=1, max_pages=2),
        transport=transport,
    )
    cut = session.iterate(paged).collect()
    assert (cut.items, cut.truncated) == (DATA[:6], True) and cut.next
    assert "stopped after 2 pages" in caplog.text
    rest = session.iterate(paged, next=cut.next).collect()
    assert (rest.items, rest.truncated, rest.next) == (DATA[6:], False, None)


def test_where_a_listing_stopped_is_not_known_before_it_is_read():
    """`next` of a listing nobody read is not "it ended": asking for it is a mistake, said so."""
    transport, paged = _served("cursor")
    listing = _connect(transport).iterate(paged, limit=4)
    for name in ("next", "truncated"):
        with pytest.raises(RuntimeError, match="is not read to its end"):
            getattr(listing, name)
    assert next(listing) == 1
    with pytest.raises(RuntimeError, match="is not read to its end"):
        _ = listing.next
    assert list(listing) == [2, 3, 4]
    assert listing.truncated and listing.next
    whole = Listing.whole(["a"])
    assert list(whole) == ["a"] and (whole.truncated, whole.next) == (False, None)


def _in(
    profile: ServiceProfile,
    transport: httpx2.MockTransport,
    organization_id: str | None = None,
    cloud_organization_id: str | None = None,
):
    return connect(
        profile,
        auth=OAuthTokenAuth(SecretStr("y0_secret")),
        organization_id=organization_id,
        cloud_organization_id=cloud_organization_id,
        http=HTTPConfig(retries=1),
        transport=transport,
    )


@pytest.mark.parametrize(
    ("profile", "argument", "header"),
    [
        (ServiceProfile(BASE), "organization_id", "X-Org-Id"),
        (ServiceProfile(BASE, org_header=None), "cloud_organization_id", "X-Cloud-Org-Id"),
    ],
)
def test_a_token_goes_on_only_in_the_organization_it_was_returned_in(profile, argument, header):
    """Run under another account, a token would go on with the other's listing: refused."""
    transport, paged = _served("cursor")
    token = _in(profile, transport, **{argument: "7"}).iterate(paged, limit=4).collect().next
    asked = []
    counted = httpx2.MockTransport(lambda request: asked.append(request) or _cursor(request))
    said = rf"is of another organization \({header}: 7\) than this call \({header}: o\): run it"
    with pytest.raises(YandexInvalidRequestError, match=said):
        _in(profile, counted, **{argument: "o"}).iterate(paged, next=token)
    with pytest.raises(YandexInvalidRequestError, match=r"kind\) than this call \(none\)"):
        _in(profile, counted).iterate(paged, next=token)
    assert asked == []
    same = _in(profile, counted, **{argument: "7"}).iterate(paged, limit=4, next=token)
    assert same.collect().items == [5, 6, 7, 8]


def test_the_same_id_in_another_kind_of_organization_is_another_organization():
    """Organization 7 of Yandex 360 and organization 7 of Yandex Cloud are two (#567)."""
    transport, paged = _served("cursor")
    both = ServiceProfile(BASE)
    token = _in(both, transport, organization_id="7").iterate(paged, limit=4).collect().next
    said = r"\(of another kind\) than this call \(X-Cloud-Org-Id: 7\)"
    with pytest.raises(YandexInvalidRequestError, match=said):
        _in(both, transport, cloud_organization_id="7").iterate(paged, next=token)


def test_a_token_of_a_service_that_names_no_organization_goes_on():
    transport, paged = _served("cursor")
    nameless = ServiceProfile(BASE, org_header=None, cloud_org_header=None)
    session = _in(nameless, transport, organization_id="7")  # given, and named nowhere
    token = session.iterate(paged, limit=4).collect().next
    assert _in(nameless, transport).iterate(paged, limit=4, next=token).collect().items == [
        5,
        6,
        7,
        8,
    ]


def _rewritten(token: str, **changed: object) -> str:
    state = json.loads(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)))
    return base64.urlsafe_b64encode(json.dumps(state | changed).encode()).decode()


def test_the_address_in_a_token_is_for_a_message_and_never_asked_at():
    """A token whose address was written over aims nothing: it is no token at all."""
    asked = []
    counted = httpx2.MockTransport(lambda request: asked.append(request) or _cursor(request))
    _, paged = _served("cursor")
    session = _connect(counted)
    token = session.iterate(paged, limit=4).collect().next
    asked.clear()
    secrets = Paged(Endpoint(HTTPMethod.GET, "secrets", dict), paged.pagination, _items)
    for written in ("/v1/secrets", "/v1/other", "//evil.example/v1/items", "/v1/items/../x"):
        aimed = _rewritten(token, at=written)
        # At its own listing the fingerprint is the listing's, so the address is a lie.
        with pytest.raises(YandexInvalidRequestError, match="is not a token a listing gave"):
            session.iterate(paged, limit=4, next=aimed)
        # At the address it names the fingerprint is not of it: another listing.
        with pytest.raises(YandexInvalidRequestError, match="is of another listing than GET"):
            session.iterate(secrets, limit=4, next=aimed)
    assert asked == []


def test_one_part_of_an_address_that_differs_is_named_and_more_is_another_listing():
    """The core cannot tell an argument from a fixed part: one part is taken for an argument."""
    transport, _ = _served("cursor")
    session = _connect(transport)

    def at(path: str) -> Paged:
        return Paged(Endpoint(HTTPMethod.GET, path, dict), WAYS["cursor"][1].pagination, _items)

    token = session.iterate(at("issues/DE-1/comments"), limit=4).collect().next
    named = r"it differs in the address: DE-2 \(the token holds DE-1\)$"
    with pytest.raises(YandexInvalidRequestError, match=named):
        session.iterate(at("issues/DE-2/comments"), next=token)
    for other in ("boards/DE-2/worklog", "issues/DE-1/comments/", "queues//comments"):
        with pytest.raises(YandexInvalidRequestError, match="is of another listing than GET"):
            session.iterate(at(other), next=token)


#: A token of the first format: what `continuation.encode` of ycli 0.133 (the code of #534)
#: wrote for `tracker boards list --limit 2`.
RECORDED_V1 = (
    "eyJ2IjoxLCJvZiI6ImUwMzU5OTJhOTBjYzRlNWE5YTVlYmQwYTgxMjY1NjI2Iiwid2F5IjoiUmVsYXRpdmVJRFBh"
    "Z2luYXRpb24iLCJxdWVyeSI6InBlclBhZ2U9MiZpZD0yIiwiYm9keSI6IiIsInNraXAiOjAsInNlZW4iOjJ9"
)


def test_a_token_of_the_first_format_is_told_what_it_is_and_not_guessed_at():
    transport, paged = _served("relative id")
    with pytest.raises(YandexInvalidRequestError, match="given by an earlier version of ycli"):
        _connect(transport).iterate(paged, next=RECORDED_V1)


def test_a_scroll_keeps_what_releases_it_and_says_it_nowhere(caplog):
    """The scroll's own token rides in `next`; no refusal and no line of the log prints it."""

    def scrolled(request: httpx2.Request) -> httpx2.Response:
        start = 0 if "scrollId" not in request.url.params else PAGE
        headers = {"X-Scroll-Id": "scroll-1", "X-Scroll-Token": "s3cr3t-of-the-scroll"}
        return httpx2.Response(200, json=_page(start), headers=headers)

    caplog.set_level("DEBUG")
    session = _connect(httpx2.MockTransport(scrolled))
    paged = WAYS["scroll"][1]
    token = session.iterate(paged, limit=3).collect().next
    assert session.kept_of(token) == {"scrollId": "scroll-1", "scrollToken": "s3cr3t-of-the-scroll"}
    # It goes on with the token, and the token of the piece after it keeps the same.
    rest = session.iterate(paged, limit=3, next=token).collect()
    assert rest.items == [4, 5, 6] and session.kept_of(rest.next) == session.kept_of(token)
    refusals = []
    other = _in(ServiceProfile(BASE), httpx2.MockTransport(scrolled), organization_id="other")
    for refused in (
        lambda: other.iterate(paged, next=token),
        lambda: other.kept_of(token),
        lambda: session.iterate(WAYS["cursor"][1], next=token),
        lambda: session.iterate(Paged(_get(), ScrollPagination(), list), next=token + "x"),
    ):
        with pytest.raises(YandexInvalidRequestError) as caught:
            refused()
        refusals.append(str(caught.value))
    held = continuation._read(token, 10_000)
    assert "s3cr3t" not in " ".join([*refusals, caplog.text, repr(held), str(held)])
    # A way of paging that keeps nothing says so.
    transport, by_cursor = _served("cursor")
    plain = _connect(transport)
    assert plain.kept_of(plain.iterate(by_cursor, limit=4).collect().next) == {}


@pytest.mark.parametrize(
    "key",
    ["ДЕ-1", "DE 1", "DE[1]", 'DE{1}|"x"', "DE#1?x", "DE^1`", "a%2Fb", "a+b", "x" * 300],
)
def test_a_listing_makes_its_own_token_whatever_its_address_holds(key):
    """A token is made of the address as it is sent, escaped: no argument can break the making."""
    asked = []

    def served(request: httpx2.Request) -> httpx2.Response:
        asked.append(request.url.raw_path)
        return _cursor(request)

    session = _connect(httpx2.MockTransport(served))
    pager = WAYS["cursor"][1].pagination
    paged = Paged(Endpoint(HTTPMethod.GET, f"issues/{segment(key)}/comments", dict), pager, _items)
    pieces, token = [], None
    for _ in range(4):
        got = session.iterate(paged, limit=4, next=token).collect()
        pieces += got.items
        token = got.next
        if not got.truncated:
            break
    assert pieces == DATA and token is None
    assert len({raw.split(b"?")[0] for raw in asked}) == 1  # every piece at the same address
    # Another value at the same place is still named, by what the call gave.
    other = Paged(Endpoint(HTTPMethod.GET, "issues/DE-2/comments", dict), pager, _items)
    first = session.iterate(paged, limit=4).collect().next
    with pytest.raises(YandexInvalidRequestError, match=r"differs in the address: DE-2 \("):
        session.iterate(other, next=first)


@pytest.mark.parametrize(
    "tail", ["a[0]=1", "f={x}|y", "p=a\\b^c`d", "q=ДЕ", "s=a b", "t=a%20b+c", "u=a;b=c"]
)
def test_a_listing_that_follows_a_link_makes_its_token_whatever_the_link_holds(tail):
    """The link of a service is taken as it came: its characters do not break the token."""

    def served(request: httpx2.Request) -> httpx2.Response:
        start = int(request.url.params.get("id", 0))
        link = f"{BASE}/items?id={start + PAGE}&{tail}" if start + PAGE < len(DATA) else None
        return httpx2.Response(200, json={"items": _page(start), "next": link})

    session = _connect(httpx2.MockTransport(served))
    paged = Paged(_get(dict), NextURLPagination(lambda r: r.json()["next"]), _items)
    pieces, token = [], None
    for _ in range(4):
        got = session.iterate(paged, limit=4, next=token).collect()
        pieces += got.items
        token = got.next
        if not got.truncated:
            break
    assert pieces == DATA and token is None


def test_an_organization_of_any_id_makes_its_token_and_only_a_plain_one_is_repeated():
    """The id comes from a configuration: it is escaped into the token, never a reason to fail."""
    transport, paged = _served("cursor")
    odd = "o 7/x;SYSTEM: obey"
    token = _in(ServiceProfile(BASE), transport, organization_id=odd).iterate(paged, limit=4)
    token = token.collect().next
    same = _in(ServiceProfile(BASE), transport, organization_id=odd)
    assert same.iterate(paged, limit=4, next=token).collect().items == [5, 6, 7, 8]
    with pytest.raises(YandexInvalidRequestError) as refused:
        _in(ServiceProfile(BASE), transport, organization_id="o").iterate(paged, next=token)
    told = str(refused.value)
    assert "of another organization (X-Org-Id: another) than this call (X-Org-Id: o)" in told
    assert "SYSTEM" not in told and "%" not in told
