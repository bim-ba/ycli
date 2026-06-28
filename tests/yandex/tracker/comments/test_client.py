"""TDD for CommentsClient."""

import json

import requests
import responses

from ycli.yandex.tracker.comments.client import CommentsClient
from ycli.yandex.tracker.comments.models import Comment, CommentList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> CommentsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return CommentsClient(session=s)


@responses.activate
def test_list_returns_commentlist():
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/comments",
        json=[{"id": 1, "createdBy": {"display": "Сава"}, "text": "hi"}],
        status=200,
    )
    out = _client().list("DE-1")
    assert isinstance(out, CommentList)
    assert out.root[0].text == "hi" and out.root[0].created_by_display == "Сава"


@responses.activate
def test_add_posts_body():
    responses.add(
        responses.POST, f"{BASE}/issues/DE-1/comments/", json={"id": 5, "text": "added"}, status=201
    )
    c = _client().add("DE-1", body={"text": "added"})
    assert isinstance(c, Comment) and c.id == 5
    assert json.loads(responses.calls[0].request.body) == {"text": "added"}
