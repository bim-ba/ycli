"""Wiki search models — the page shape the live API returned, and the requests built from them."""

import pytest
from pydantic import ValidationError

from ycli.yandex.wiki.search.models import SearchDateRange, SearchFilters, SearchPage, SearchRequest


def test_a_result_page_parses_as_the_api_prints_it():
    page = SearchPage.model_validate(
        {
            "results": [
                {
                    "url": "/users/ivan",
                    "slug": "users/ivan",
                    "title": "<em>Ivan</em>",
                    "content": "Personal page",
                    "type": "page",
                    "modified_at": "2026-07-10T13:59:44",
                }
            ],
            "next_cursor": "2",
            "prev_cursor": None,
        }
    )
    assert page.results[0].slug == "users/ivan" and page.results[0].type == "page"
    assert (page.next_cursor, page.prev_cursor) == ("2", None)


def test_a_date_window_may_have_one_end_or_both():
    window = SearchDateRange.model_validate({"from": "2026-01-01", "to": "2026-02-01"})
    assert window.model_dump(mode="json") == {
        "from": "2026-01-01T00:00:00",
        "to": "2026-02-01T00:00:00",
    }
    only_start = SearchDateRange.model_validate({"from": "2026-01-01"})
    assert only_start.model_dump(mode="json", exclude_none=True) == {"from": "2026-01-01T00:00:00"}
    only_end = SearchDateRange.model_validate({"to": "2026-02-01"})
    assert only_end.model_dump(mode="json", exclude_none=True) == {"to": "2026-02-01T00:00:00"}


def test_a_request_dumps_dates_as_text_and_keeps_the_defaults():
    request = SearchRequest(
        query="plan",
        filters=SearchFilters(
            created_at=SearchDateRange.model_validate({"from": "2026-01-01", "to": "2026-02-01"})
        ),
    )
    assert request.model_dump(mode="json", exclude_none=True) == {
        "query": "plan",
        "filters": {
            "created_at": {"from": "2026-01-01T00:00:00", "to": "2026-02-01T00:00:00"},
            "show_obsolete": False,
        },
        "cursor": 1,
        "limit": 10,
        "order_by": "relevancy",
        "highlight": False,
    }


@pytest.mark.parametrize(
    "given", [{"query": ""}, {"limit": 51}, {"limit": 0}, {"cursor": 501}, {"cursor": 0}]
)
def test_a_request_outside_the_api_limits_is_kept_as_given(given):
    request = SearchRequest.model_validate({"query": "x", **given})
    for name, value in given.items():
        assert getattr(request, name) == value


def test_a_request_without_a_query_is_refused():
    with pytest.raises(ValidationError) as refused:
        SearchRequest.model_validate({})
    assert [(e["type"], e["loc"]) for e in refused.value.errors()] == [("missing", ("query",))]
