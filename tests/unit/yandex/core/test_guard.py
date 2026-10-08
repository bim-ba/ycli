"""The rule every write goes through lives in the core: no surface is needed to keep it."""

import asyncio
from http import HTTPMethod

import pytest
from pydantic import SecretStr

from tests.mock_api import MockAPI
from ycli.settings import HTTPConfig
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Effect, Endpoint, Paged
from ycli.yandex.core.guard import Guard, PlannedRequest, RequestPlanned
from ycli.yandex.core.pagination import PageNumberPagination
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect, connect_async
from ycli.yandex.errors import YandexDeclinedError

ITEMS = "https://api.test/v1/items"
GET = Endpoint(HTTPMethod.GET, "items", list[int])
PATCH = Endpoint(HTTPMethod.PATCH, "items/1", json={"name": "new"})
DELETE = Endpoint(HTTPMethod.DELETE, "items/1")
# A search is a POST that only reads: the effect says so, not the method.
SEARCH = Endpoint(HTTPMethod.POST, "items/_search", list[int], effect=Effect.READ)


def _api() -> MockAPI:
    api = MockAPI()
    api.add("GET", ITEMS, json=[1])
    api.add("POST", f"{ITEMS}/_search", json=[1])
    api.add("PATCH", f"{ITEMS}/1", json={})
    api.add("DELETE", f"{ITEMS}/1", status=204)
    return api


def _session(api: MockAPI, guard: Guard | None, factory=connect):
    return factory(
        ServiceProfile("https://api.test/v1"),
        auth=OAuthTokenAuth(SecretStr("t")),
        http=HTTPConfig(retries=0),
        transport=api.transport(),
        guard=guard,
    )


def test_with_no_guard_everything_is_sent():
    api = _api()
    session = _session(api, None)
    for operation in (GET, SEARCH, PATCH, DELETE):
        session.send(operation)
    assert [call.method for call in api.calls] == ["GET", "POST", "PATCH", "DELETE"]


def test_a_dry_run_sends_the_reads_and_stops_at_the_first_write_with_its_plan():
    api = _api()
    session = _session(api, Guard(dry_run=True))
    assert session.send(GET) == [1] and session.send(SEARCH) == [1]
    for operation, method in ((PATCH, "PATCH"), (DELETE, "DELETE")):
        with pytest.raises(RequestPlanned) as planned:
            session.send(operation)
        assert planned.value.plan.method == method
    assert planned.value.plan == PlannedRequest(method="DELETE", url=f"{ITEMS}/1", body=None)
    assert [call.method for call in api.calls] == ["GET", "POST"]  # no write went out


def test_what_destroys_data_is_confirmed_and_nothing_else_is():
    api = _api()
    asked: list[PlannedRequest] = []

    def confirm(plan: PlannedRequest) -> bool:
        asked.append(plan)
        return True

    session = _session(api, Guard(confirm=confirm))
    for operation in (GET, SEARCH, PATCH, DELETE):
        session.send(operation)
    assert [(plan.method, plan.url) for plan in asked] == [("DELETE", f"{ITEMS}/1")]
    assert len(api.calls) == 4


def test_a_delete_that_is_not_confirmed_is_not_sent():
    api = _api()
    session = _session(api, Guard(confirm=lambda plan: False))
    with pytest.raises(YandexDeclinedError, match="was not confirmed; nothing was sent"):
        session.send(DELETE)
    assert api.calls == []
    session.send(PATCH)  # a write that destroys nothing is not asked about
    assert [call.method for call in api.calls] == ["PATCH"]


def test_a_dry_run_shows_a_delete_before_anybody_is_asked():
    session = _session(_api(), Guard(dry_run=True, confirm=lambda plan: False))
    with pytest.raises(RequestPlanned):
        session.send(DELETE)


def test_a_listing_is_checked_once_and_a_listing_that_writes_is_planned():
    api = _api()
    listing = Paged(GET, PageNumberPagination(page_size=5), list)
    assert list(_session(api, Guard(dry_run=True)).iterate(listing)) == [1]
    writing = Paged(Endpoint(HTTPMethod.POST, "items", list[int]), listing.pagination, list)
    with pytest.raises(RequestPlanned):
        _session(api, Guard(dry_run=True)).iterate(writing)


def test_an_asynchronous_session_keeps_the_same_rule():
    async def run() -> list[str]:
        api = _api()
        session = _session(api, Guard(dry_run=True), connect_async)
        assert await session.send(GET) == [1]
        with pytest.raises(RequestPlanned):
            await session.send(PATCH)
        with pytest.raises(RequestPlanned):
            session.iterate(Paged(PATCH, PageNumberPagination(page_size=5), list))
        return [call.method for call in api.calls]

    assert asyncio.run(run()) == ["GET"]
