"""The asynchronous API of the SDK: ``connect_async`` and a resource's ``endpoints`` (#321).

``docs/en/how-to/call-the-api-asynchronously.md`` shows these calls; this file holds them to
the same requests and results the synchronous clients give.
"""

import asyncio

from pydantic import SecretStr

from tests.hosts import TRACKER_BASE, WIKI_BASE
from tests.mock_api import MockAPI
from ycli.yandex import tracker, wiki
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.session import AsyncSession, connect_async
from ycli.yandex.tracker.boards import endpoints as boards
from ycli.yandex.tracker.issues import endpoints as issues
from ycli.yandex.tracker.issues.models import IssueSearch
from ycli.yandex.wiki.pages import endpoints as pages


def _tracker(api: MockAPI) -> AsyncSession:
    return connect_async(
        tracker.SERVICE.profile,
        auth=OAuthTokenAuth(SecretStr("token")),
        organization_id="8526809",
        transport=api.transport(),
    )


async def test_one_operation_is_sent_and_parsed_into_its_model():
    api = MockAPI()
    api.add("GET", f"{TRACKER_BASE}/boards/31", json={"id": 31, "name": "Kanban"})
    session = _tracker(api)
    board = await session.send(boards.get(31))
    await session.aclose()
    assert (board.id, board.name) == (31, "Kanban")
    assert api.calls[0].headers["X-Org-Id"] == "8526809"
    assert api.calls[0].headers["Authorization"] == "OAuth token"


async def test_a_listing_is_walked_page_by_page():
    api = MockAPI()
    url = f"{TRACKER_BASE}/issues/_search"
    api.add("POST", url, json=[{"key": "DE-1"}, {"key": "DE-2"}], headers={"X-Total-Pages": "2"})
    api.add("POST", url, json=[{"key": "DE-3"}], headers={"X-Total-Pages": "2"})
    session = _tracker(api)
    search = issues.search(IssueSearch(filter={"queue": "DE"}), expand=None, page_size=2)
    keys = [issue.key async for issue in session.iterate(search)]
    await session.aclose()
    assert keys == ["DE-1", "DE-2", "DE-3"]
    assert [call.url.params["page"] for call in api.calls] == ["1", "2"]


async def test_calls_run_concurrently_on_one_session():
    api = MockAPI()
    for slug in ("team/a", "team/b", "team/c"):
        api.add("GET", f"{WIKI_BASE}/pages", json={"id": 1, "slug": slug, "title": slug})
    session = connect_async(
        wiki.SERVICE.profile, auth=OAuthTokenAuth(SecretStr("token")), transport=api.transport()
    )
    found = await asyncio.gather(
        *(
            session.send(pages.get(slug, fields=None, revision_id=None, raise_on_redirect=False))
            for slug in ("team/a", "team/b", "team/c")
        )
    )
    await session.aclose()
    assert len(found) == 3
    assert sorted(call.url.params["slug"] for call in api.calls) == ["team/a", "team/b", "team/c"]
