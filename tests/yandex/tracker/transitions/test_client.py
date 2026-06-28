"""TDD for TransitionsClient."""

import json

import requests
import responses

from ycli.yandex.tracker.transitions.client import TransitionsClient
from ycli.yandex.tracker.transitions.models import TransitionList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> TransitionsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return TransitionsClient(session=s)


@responses.activate
def test_list_returns_transitionlist():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/transitions",
        json=[{"id": "close", "display": "Close"}],
        status=200,
    )
    out = _client().list("DE-1")
    assert isinstance(out, TransitionList)
    assert out.root[0].id == "close"


@responses.activate
def test_execute_posts_body_returns_transitionlist():
    responses.add(
        responses.POST,
        f"{BASE}/issues/DE-1/transitions/close/_execute",
        json=[
            {
                "self": "https://api.tracker.yandex.net/v3/issues/DE-1/transitions/close",
                "id": "close",
                "to": {"id": "3", "key": "closed", "display": "Closed"},
                "screen": {"id": "scr1"},
            }
        ],
        status=200,
    )
    out = _client().execute("DE-1", "close", body={"comment": "done"})
    assert isinstance(out, TransitionList)
    assert out.root[0].id == "close"
    assert out.root[0].to is not None
    assert out.root[0].to.key == "closed"
    assert out.root[0].to.display == "Closed"
    assert json.loads(responses.calls[0].request.body) == {"comment": "done"}  # ty: ignore[invalid-argument-type]
