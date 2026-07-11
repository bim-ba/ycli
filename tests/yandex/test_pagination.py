from ycli.yandex.pagination import (
    CursorStrategy,
    NextUrlStrategy,
    OffsetStrategy,
    RelativeCursorStrategy,
    resolve_cap,
)


def test_resolve_cap_all_flag_uncaps():
    assert resolve_cap(0, 500, all_=True) is None
    assert resolve_cap(10, 500, all_=True) is None


def test_resolve_cap_limit_wins_then_default():
    assert resolve_cap(10, 500) == 10
    assert resolve_cap(0, 500) == 500


def test_cursor_strategy_drains_until_no_cursor():
    pages = {
        None: {"results": [1, 2], "next_cursor": "c1"},
        "c1": {"results": [3, 4], "next_cursor": None},
    }
    out = CursorStrategy(
        extract=lambda p: p["results"], next_of=lambda p: p["next_cursor"]
    ).collect(lambda cursor: pages[cursor], limit=None)
    assert out == [1, 2, 3, 4]


def test_cursor_strategy_respects_limit():
    pages = {None: {"results": [1, 2, 3, 4], "next_cursor": "c1"}}
    out = CursorStrategy(
        extract=lambda p: p["results"], next_of=lambda p: p["next_cursor"]
    ).collect(lambda cursor: pages[cursor], limit=3)
    assert out == [1, 2, 3]  # stops without fetching c1


def test_cursor_strategy_empty_string_cursor_is_not_terminal():
    """Only ``None`` terminates: an empty-string cursor is a real cursor, fetched onward.

    Locks the deliberate ``if cursor is None`` contract (vs the old falsy ``if not cursor``,
    which would have stopped at the empty string) against a future regression.
    """
    pages = {
        None: {"results": [1], "next_cursor": ""},
        "": {"results": [2], "next_cursor": None},
    }
    out = CursorStrategy(
        extract=lambda p: p["results"], next_of=lambda p: p["next_cursor"]
    ).collect(lambda cursor: pages[cursor], limit=None)
    assert out == [1, 2]  # "" is followed, not treated as exhausted


def test_next_url_strategy_drains_and_dedupes_self_loops():
    pages = {
        "start": {"answers": [1], "next": {"next_url": "p2"}},
        "p2": {"answers": [2], "next": {"next_url": "p2"}},  # self-loop guard
    }
    out = NextUrlStrategy(
        extract=lambda p: p["answers"],
        next_url_of=lambda p: (p["next"] or {}).get("next_url"),
        fetch_url=lambda url: pages[url],
    ).collect(lambda cursor: pages["start"], limit=None)
    assert out == [1, 2]


def test_cursor_collect_wrapped_extracts_wraps_next_and_bounds():
    pages = {
        None: {"results": [1, 2], "next_cursor": "c1"},
        "c1": {"results": [3, 4], "next_cursor": None},
    }
    out = CursorStrategy.collect_wrapped(
        lambda cursor: pages[cursor],
        extract=lambda p: p["results"],
        next_of=lambda p: p["next_cursor"],
        wrap=list,
        limit=3,
    )
    assert out == [1, 2, 3]


def test_next_url_strategy_respects_limit():
    pages = {
        "start": {"answers": [1, 2], "next": {"next_url": "p2"}},
        "p2": {"answers": [3, 4], "next": {"next_url": "p3"}},
        "p3": {"answers": [5], "next": None},
    }
    out = NextUrlStrategy(
        extract=lambda p: p["answers"],
        next_url_of=lambda p: (p["next"] or {}).get("next_url"),
        fetch_url=lambda url: pages[url],
    ).collect(lambda cursor: pages["start"], limit=2)
    assert out == [1, 2]  # stops before fetching p2


# --- OffsetStrategy ---------------------------------------------------------------------


def _offset_pages(*pages: list[int]):
    """A fetch_page(offset) that returns a scripted page keyed by integer offset."""
    by_offset = {index * 2: page for index, page in enumerate(pages)}
    return lambda offset: {"result": by_offset[offset]}


def test_offset_single_short_page_stops_after_one_fetch():
    calls: list[int] = []

    def fetch(offset):
        calls.append(offset)
        return {"result": [1]}

    out = OffsetStrategy(extract=lambda p: p["result"], page_size=2).collect(fetch, limit=None)
    assert out == [1]  # a page shorter than page_size ends the walk
    assert calls == [0]


def test_offset_drains_full_then_short_page():
    calls: list[int] = []

    def fetch(offset):
        calls.append(offset)
        return {"result": [1, 2]} if offset == 0 else {"result": [3]}

    out = OffsetStrategy(extract=lambda p: p["result"], page_size=2).collect(fetch, limit=None)
    assert out == [1, 2, 3]
    assert calls == [0, 2]  # offset advanced by page_size after the full first page


def test_offset_full_then_empty_page_boundary():
    calls: list[int] = []

    def fetch(offset):
        calls.append(offset)
        return {"result": [1, 2]} if offset == 0 else {"result": []}

    out = OffsetStrategy(extract=lambda p: p["result"], page_size=2).collect(fetch, limit=None)
    assert out == [1, 2]  # exact multiple of page_size → one extra (empty) request
    assert calls == [0, 2]


def test_offset_respects_limit_across_a_page_boundary():
    out = OffsetStrategy(extract=lambda p: p["result"], page_size=2).collect(
        _offset_pages([1, 2], [3, 4]), limit=3
    )
    assert out == [1, 2, 3]  # truncated mid-second-page


def test_offset_empty_first_page_returns_nothing():
    calls: list[int] = []

    def fetch(offset):
        calls.append(offset)
        return {"result": []}

    out = OffsetStrategy(extract=lambda p: p["result"], page_size=2).collect(fetch, limit=None)
    assert out == []
    assert calls == [0]  # one fetch, no advance


# --- RelativeCursorStrategy -------------------------------------------------------------


def test_relative_cursor_single_page_then_empty_terminates():
    pages = {
        None: [{"id": "1"}, {"id": "2"}],
        "2": [],  # requesting id=2 returns nothing → done
    }
    out = RelativeCursorStrategy(
        extract=lambda p: p,
        id_of=lambda item: item["id"],
    ).collect(lambda cursor: pages[cursor], limit=None)
    assert [item["id"] for item in out] == ["1", "2"]


def test_relative_cursor_drains_multiple_pages():
    pages = {
        None: [{"id": "a"}, {"id": "b"}],
        "b": [{"id": "c"}, {"id": "d"}],
        "d": [],
    }
    out = RelativeCursorStrategy(
        extract=lambda p: p,
        id_of=lambda item: item["id"],
    ).collect(lambda cursor: pages[cursor], limit=None)
    assert [item["id"] for item in out] == ["a", "b", "c", "d"]


def test_relative_cursor_respects_limit_across_a_boundary():
    pages = {
        None: [{"id": "1"}, {"id": "2"}],
        "2": [{"id": "3"}, {"id": "4"}],
    }
    out = RelativeCursorStrategy(
        extract=lambda p: p,
        id_of=lambda item: item["id"],
    ).collect(lambda cursor: pages[cursor], limit=3)
    assert [item["id"] for item in out] == ["1", "2", "3"]  # stops mid-second-page


def test_relative_cursor_empty_first_page_returns_nothing():
    out = RelativeCursorStrategy(
        extract=lambda p: p,
        id_of=lambda item: item["id"],
    ).collect(lambda cursor: [], limit=None)
    assert out == []


def test_relative_cursor_last_item_without_id_terminates():
    out = RelativeCursorStrategy(
        extract=lambda p: p,
        id_of=lambda item: item.get("id"),  # last item yields None → stop
    ).collect(lambda cursor: [{"id": None}], limit=None)
    assert out == [{"id": None}]
