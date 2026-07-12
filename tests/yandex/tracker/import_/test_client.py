"""TDD for ImportClient — JSON imports assert the sent body; the file import is multipart."""

import json

import requests
import responses

from ycli.yandex.tracker.attachments.models import Attachment
from ycli.yandex.tracker.comments.models import Comment
from ycli.yandex.tracker.import_.client import ImportClient
from ycli.yandex.tracker.issues.models import Issue
from ycli.yandex.tracker.links.models import Link
from ycli.yandex.tracker.worklog.models import WorklogList

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> ImportClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return ImportClient(session=session)


@responses.activate
def test_task_posts_body_and_returns_issue():
    responses.add(responses.POST, f"{BASE}/issues/_import", json={"key": "TEST-1"}, status=200)
    issue = _client().task(
        body={"queue": "TEST", "summary": "Test", "createdAt": "t", "createdBy": "11"}
    )
    assert isinstance(issue, Issue) and issue.key == "TEST-1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "queue": "TEST",
        "summary": "Test",
        "createdAt": "t",
        "createdBy": "11",
    }


@responses.activate
def test_comment_posts_body_and_returns_comment():
    responses.add(
        responses.POST,
        f"{BASE}/issues/TEST-1/comments/_import",
        json={"id": 1, "text": "T"},
        status=200,
    )
    out = _client().comment("TEST-1", body={"text": "T", "createdAt": "t", "createdBy": "11"})
    assert isinstance(out, Comment) and out.text == "T"


@responses.activate
def test_link_posts_body_and_returns_link():
    responses.add(
        responses.POST,
        f"{BASE}/issues/TEST-1/links/_import",
        json={"id": 1, "object": {"key": "TEST-2"}},
        status=200,
    )
    out = _client().link(
        "TEST-1",
        body={"relationship": "relates", "issue": "TEST-2", "createdAt": "t", "createdBy": "11"},
    )
    assert isinstance(out, Link) and out.object_key == "TEST-2"


@responses.activate
def test_worklog_posts_to_plural_path_and_parses_array_response():
    # The live endpoint answers with a JSON ARRAY of created records (regression: a single
    # Worklog model choked on it with a pydantic validation error).
    responses.add(
        responses.POST,
        f"{BASE}/issues/TEST-1/worklogs/_import",
        json=[{"id": 37, "duration": "PT1H"}],
        status=200,
    )
    out = _client().worklog(
        "TEST-1", body={"duration": "PT1H", "createdAt": "t", "createdBy": "u", "start": "s"}
    )
    assert isinstance(out, WorklogList) and out.root[0].duration == "PT1H"
    assert (responses.calls[0].request.url or "").endswith("/worklogs/_import")


@responses.activate
def test_file_uploads_multipart_with_query_params():
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/attachments/_import",
        json={"id": "123", "name": "pic.png"},
        status=200,
    )
    out = _client().file(
        "JUNE-2", filename="pic.png", created_at="2020-01-01", created_by="user", data=b"PNGDATA"
    )
    assert isinstance(out, Attachment) and out.name == "pic.png"
    request = responses.calls[0].request
    assert "filename=pic.png" in request.url  # ty: ignore[unsupported-operator]
    assert "createdAt=2020-01-01" in request.url  # ty: ignore[unsupported-operator]
    assert "createdBy=user" in request.url  # ty: ignore[unsupported-operator]
    assert request.headers["Content-Type"].startswith("multipart/form-data")  # ty: ignore[invalid-argument-type]
    body = request.body
    body = body.read() if hasattr(body, "read") else body  # ty: ignore[call-non-callable]
    assert (
        b"PNGDATA" in body  # ty: ignore[unsupported-operator]
    )  # the raw file bytes ride in the multipart part
