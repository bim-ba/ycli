"""A call that goes on gives only what is required: that must never be refused by itself (#559).

With ``next`` the optional arguments are not given, so the request the call builds is the one
of its required arguments alone, and the token holds the request of the fuller first call. The
check of the core (:mod:`ycli.yandex.core.continuation`) refuses what the token does not hold,
so for every listing and each of its optional arguments the request of the required alone has
to lie within the request with that argument. A listing that sends a default beside an
optional argument (a type of scroll, a sort order, a flag), or a page size of its own that the
limit shapes, fails here, not at a user's second page.

One thing it cannot see: a constant page size put back into the operation of a listing that
follows a link of the service (`forms notifications list`). It differs from nothing here, and
is refused only when the link names another size; the pager owns it for that reason.
"""

from typing import Any

import httpx2
import pytest
from fastmcp import Client

from tests.full_server import mcp as full
from ycli.yandex.core import continuation
from ycli.yandex.core import session as core
from ycli.yandex.core.continuation import HANDLES
from ycli.yandex.core.listing import Listing

#: Not a listing once given: ``selected`` asks for one window around an event, in one reply.
ONE_REPLY = {("tracker_entities_events_list", "selected")}


def _values(name: str, schema: dict[str, Any], number: int) -> list[Any]:
    """Values the schema of an argument takes: every one where they are few, else some one.

    Every value of a boolean and of an enumeration, because a default the operation sends in
    its place is one of them, and a probe that happens to equal it would see nothing.
    """
    schema = next((one for one in schema.get("anyOf", []) if one.get("type") != "null"), schema)
    if "enum" in schema:
        return list(schema["enum"])
    match schema.get("type"):
        case "integer":
            return [987650 + number]
        case "boolean":
            return [True, False]
        case "array":
            return [[f"zz-{name}"]]
        case "string":
            return ["2026-01-01T00:00:00Z" if name in {"from_", "to"} else f"zz-{name}"]
    return [{}]  # a body: every field of it is optional


async def test_what_is_required_alone_lies_within_the_request_of_every_fuller_call(
    api, monkeypatch
):
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")
    asked: list[httpx2.Request] = []

    def iterate(self, paged, *, limit=None, next=None):
        asked.append(paged.endpoint.request(self._client))
        return Listing.whole([])

    monkeypatch.setattr(core.SyncSession, "iterate", iterate)
    listings, unasked, refused = 0, set(), []
    async with Client(full) as client:

        async def request_of(tool: str, arguments: dict[str, object]) -> httpx2.Request | None:
            asked.clear()
            await client.call_tool(tool, arguments, raise_on_error=False)
            return asked[0] if asked else None

        for tool in await client.list_tools():
            properties = tool.input_schema.get("properties", {})
            if not {"limit", "next"} <= properties.keys():  # a listing has both
                continue
            listings += 1
            # One of the two credentials is given: DataLens takes the IAM token, the rest OAuth.
            ours, other = "YANDEX_ID_OAUTH_TOKEN", "YANDEX_CLOUD_IAM_TOKEN"
            if tool.name.startswith("datalens_"):
                ours, other = other, ours
            monkeypatch.setenv(ours, "t")
            monkeypatch.delenv(other, raising=False)
            required = tool.input_schema.get("required", [])
            alone = {name: _values(name, properties[name], 0)[0] for name in required}
            base = await request_of(tool.name, alone)
            assert base is not None, f"{tool.name} did not ask with {alone}"
            # The limit is given beside `next` and shapes the page of many listings: it is
            # tried like an optional argument, so a page size the operation sends is seen.
            beside = [*sorted(properties.keys() - set(required) - HANDLES), "limit"]
            tried = [
                (name, value)
                for number, name in enumerate(beside, 1)
                for value in ([7] if name == "limit" else _values(name, properties[name], number))
            ]
            for name, value in tried:
                fuller = await request_of(tool.name, {**alone, name: value})
                if fuller is None:
                    unasked.add((tool.name, name))
                    continue
                held = continuation.Continuation(
                    v=2,
                    of="",
                    at="/",
                    org="",
                    way="",
                    query=fuller.url.query.decode(),
                    body=fuller.content.decode(),
                    skip=0,
                    seen=0,
                    kept={},
                )
                if differing := continuation._differing(base, held):
                    refused.append(f"{tool.name} with {name}={value!r}: {differing}")
    assert listings > 40
    assert not refused, "a call that goes on would be refused for what it did not give"
    assert unasked == ONE_REPLY


def test_the_check_sees_a_default_sent_beside_an_optional_argument():
    """What this file guards against, on a listing made to do it: the check is not blind."""
    first = httpx2.Request("POST", "https://x/s?scrollType=unsorted", json={"query": "a"})
    token = continuation.encode(first, first, way="ScrollPagination", skip=0, seen=0)
    again = httpx2.Request("POST", "https://x/s?scrollType=sorted", json={"query": "a"})
    with pytest.raises(Exception, match="it differs in: scrollType"):
        continuation.resume(again, first, token, way="ScrollPagination", longest=1000)
