"""TDD for RemoteLinksClient — responses stub + session DI (list/create/delete)."""

import json

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.remotelinks.client import RemoteLinksClient
from ycli.yandex.tracker.remotelinks.models import RemoteLink, RemoteLinkList


def _client() -> RemoteLinksClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return RemoteLinksClient(session=session)


@responses.activate
def test_list_returns_remote_links():
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/remotelinks",
        json=[{"id": 51, "object": {"key": "TEST-17"}}],
        status=200,
    )
    out = _client().list("JUNE-2")
    assert isinstance(out, RemoteLinkList)
    assert out.root[0].object_key == "TEST-17"


@responses.activate
def test_create_posts_body_with_backlink_query():
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/remotelinks",
        json={"id": 51, "object": {"key": "TEST-17"}},
        status=201,
    )
    link = _client().create(
        "JUNE-2",
        body={"relationship": "RELATES", "key": "TEST-17", "origin": "ru.yandex.bitbucket"},
        backlink="true",
    )
    assert isinstance(link, RemoteLink)
    assert link.object_key == "TEST-17"
    assert "backlink=true" in responses.calls[0].request.url  # ty: ignore[unsupported-operator]
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "relationship": "RELATES",
        "key": "TEST-17",
        "origin": "ru.yandex.bitbucket",
    }


@responses.activate
def test_delete_returns_none():
    responses.add(responses.DELETE, f"{BASE}/issues/JUNE-2/remotelinks/51", status=204)
    assert _client().delete("JUNE-2", "51") is None
    assert responses.calls[0].request.method == "DELETE"
