"""Contract cases for Wiki ``/search``, sent by ``pages.search`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.wiki.pages.models import SearchRequest

HIT = {
    "url": "/team/roadmap",
    "slug": "team/roadmap",
    "title": "<em>Roadmap</em> 2026",
    "content": "The <em>roadmap</em> for the year",
    "type": "page",
    "modified_at": "2026-10-02T20:11:07",
}
FILE_HIT = {**HIT, "url": "/team/spec.pdf", "slug": "team/spec", "title": "Spec", "type": "file"}

FILTERS = {
    "type": "page",
    "authors": [{"uid": "9101"}, {"cloud_uid": "cloud-9102"}],
    "cluster": "team/handbook",
    "created_at": {"from": "2026-01-01T00:00:00", "to": "2026-02-01T00:00:00"},
    "modified_at": {"from": "2026-03-01T00:00:00", "to": "2026-04-01T00:00:00"},
    "show_obsolete": True,
}
FULL_BODY = {
    "query": "quarterly roadmap",
    "filters": FILTERS,
    "cursor": 3,
    "limit": 25,
    "order_by": "modified_date",
    "highlight": True,
}

SEARCH_CASES = [
    Case(
        "wiki.pages.search",
        args=(SearchRequest.model_validate(FULL_BODY),),
        cli=[
            "wiki",
            "pages",
            "search",
            "quarterly roadmap",
            "--type",
            "page",
            "--cluster",
            "team/handbook",
            "--author-uid",
            "9101",
            "--author-cloud-uid",
            "cloud-9102",
            "--created-from",
            "2026-01-01",
            "--created-to",
            "2026-02-01",
            "--modified-from",
            "2026-03-01",
            "--modified-to",
            "2026-04-01",
            "--show-obsolete",
            "--order-by",
            "modified_date",
            "--highlight",
            "--limit",
            "25",
            "--cursor",
            "3",
        ],
        mcp=(
            "wiki_pages_search",
            {
                "text": "quarterly roadmap",
                "filters": FILTERS,
                "order_by": "modified_date",
                "highlight": True,
                "limit": 25,
                "cursor": 3,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "search", json=FULL_BODY),
                Reply(json={"results": [HIT, FILE_HIT], "next_cursor": "4", "prev_cursor": "2"}),
            )
        ],
    ),
    Case(
        "wiki.pages.search",
        args=(
            SearchRequest.model_validate(
                {
                    "query": "budget",
                }
            ),
        ),
        cli=["wiki", "pages", "search", "budget"],
        mcp=None,
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "search",
                    json={
                        "query": "budget",
                    },
                ),
                Reply(json={"results": [], "next_cursor": "2", "prev_cursor": None}),
            )
        ],
    ),
    Case(
        "wiki.pages.search",
        args=(
            SearchRequest.model_validate(
                {
                    "query": "onboarding",
                }
            ),
        ),
        cli=None,
        mcp=("wiki_pages_search", {"text": "onboarding"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "search",
                    json={
                        "query": "onboarding",
                    },
                ),
                Reply(json={"results": [FILE_HIT], "next_cursor": None, "prev_cursor": None}),
            )
        ],
    ),
]
