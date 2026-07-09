"""TDD for UsersClient — single get + relative-cursor draining of /users/_relative."""

import json
from urllib.parse import parse_qs, urlparse

import requests
import responses

from ycli.yandex.tracker.users.client import UsersClient
from ycli.yandex.tracker.users.models import User, UserList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> UsersClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return UsersClient(session=s)


@responses.activate
def test_get_parses_user_and_passes_expand():
    responses.add(
        responses.GET,
        f"{BASE}/users/username",
        json={"uid": 12, "login": "username", "display": "Ivan Ivanov", "dismissed": False},
        status=200,
    )
    out = _client().get(login_or_id="username", expand="groups")
    assert isinstance(out, User)
    assert out.uid == 12 and out.login == "username" and out.display == "Ivan Ivanov"
    assert responses.calls[0].request.params["expand"] == "groups"  # ty: ignore[unresolved-attribute]


def _drain_callback(request):
    """Three-request stub: pages keyed off the ``id`` cursor, terminating on an empty page."""
    params = parse_qs(urlparse(request.url).query)
    cursor = params.get("id", [None])[0]
    if cursor is None:
        body = {"users": [{"uid": 1, "login": "a"}, {"uid": 2, "login": "b"}], "hasNext": True}
    elif cursor == "2":
        body = {"users": [{"uid": 3, "login": "c"}], "hasNext": True}
    else:
        body = {"users": [], "hasNext": False}
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_drains_relative_cursor_across_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/users/_relative",
        callback=_drain_callback,
        content_type="application/json",
    )
    out = _client().list()
    assert isinstance(out, UserList)
    assert [u.uid for u in out.root] == [1, 2, 3]  # concatenated in order across pages
    assert len(responses.calls) == 3  # page1 + page2(id=2) + empty terminator(id=3)
    assert responses.calls[0].request.params["perPage"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_respects_limit_without_extra_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/users/_relative",
        json={"users": [{"uid": 1}, {"uid": 2}], "hasNext": True},
        status=200,
    )
    out = _client().list(limit=1)
    assert [u.uid for u in out.root] == [1]  # truncated to the limit
    assert len(responses.calls) == 1  # limit satisfied by page 1 — no second request


@responses.activate
def test_list_stops_when_last_user_has_no_uid():
    responses.add(
        responses.GET,
        f"{BASE}/users/_relative",
        json={"users": [{"login": "no-uid"}], "hasNext": True},
        status=200,
    )
    out = _client().list()
    assert [u.login for u in out.root] == ["no-uid"]  # no uid cursor → walk ends
    assert len(responses.calls) == 1
