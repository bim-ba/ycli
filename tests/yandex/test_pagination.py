from ycli.yandex.pagination import (
    CursorStrategy,
    NextUrlStrategy,
    SinglePageStrategy,
)


def test_single_page_truncates_to_limit():
    page = {"results": [1, 2, 3, 4]}
    out = SinglePageStrategy(extract=lambda p: p["results"]).collect(lambda cursor: page, limit=2)
    assert out == [1, 2]


def test_single_page_none_limit_returns_all():
    page = {"results": [1, 2, 3]}
    out = SinglePageStrategy(extract=lambda p: p["results"]).collect(
        lambda cursor: page, limit=None
    )
    assert out == [1, 2, 3]


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


def test_single_page_collect_wrapped_extracts_wraps_and_bounds():
    pages = {"a": [1, 2, 3]}
    out = SinglePageStrategy.collect_wrapped(
        lambda cursor: pages, extract=lambda p: p["a"], wrap=list, limit=2
    )
    assert out == [1, 2]


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
