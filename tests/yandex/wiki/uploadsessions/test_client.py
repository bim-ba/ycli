"""Transport tests for the Wiki /upload_sessions client (responses stub + session DI)."""

import json

import requests
import responses

from ycli.yandex.wiki.uploadsessions.client import UploadSessionsClient
from ycli.yandex.wiki.uploadsessions.models import (
    AbortActiveUploadsResult,
    UploadSession,
    UploadSessionCreate,
)

BASE = "https://api.wiki.yandex.net/v1"

_SESSION_JSON = {
    "session_id": "s-1",
    "file_name": "d.png",
    "file_size": 2048,
    "status": "in_progress",
    "storage_type": "mds",
}


def _client():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return UploadSessionsClient(session=s)


@responses.activate
def test_create_posts_typed_body():
    responses.add(responses.POST, f"{BASE}/upload_sessions", json=_SESSION_JSON, status=200)
    out = _client().create(UploadSessionCreate(file_name="d.png", file_size=2048))
    assert isinstance(out, UploadSession)
    assert out.session_id == "s-1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "file_name": "d.png",
        "file_size": 2048,
    }


@responses.activate
def test_get_returns_session():
    responses.add(responses.GET, f"{BASE}/upload_sessions/s-1", json=_SESSION_JSON, status=200)
    out = _client().get(session_id="s-1")
    assert out.status == "in_progress"
    assert responses.calls[0].request.url.endswith("/upload_sessions/s-1")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_upload_part_sends_raw_octet_stream_bytes():
    responses.add(
        responses.PUT, f"{BASE}/upload_sessions/s-1/upload_part", json=_SESSION_JSON, status=200
    )
    payload = b"\x89PNG\r\n\x1a\n raw part bytes"
    out = _client().upload_part("s-1", part_number=1, data=payload)
    assert isinstance(out, UploadSession)
    request = responses.calls[0].request
    assert request.method == "PUT"
    assert request.headers["Content-Type"] == "application/octet-stream"
    assert request.body == payload  # verbatim bytes — no JSON/multipart wrapping
    assert request.params["part_number"] == "1"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_upload_part_carries_part_number():
    responses.add(
        responses.PUT, f"{BASE}/upload_sessions/s-1/upload_part", json=_SESSION_JSON, status=200
    )
    _client().upload_part("s-1", part_number=3, data=b"tail")
    assert responses.calls[0].request.params["part_number"] == "3"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_finish_posts_and_returns_session():
    finished = {**_SESSION_JSON, "status": "finished"}
    responses.add(responses.POST, f"{BASE}/upload_sessions/s-1/finish", json=finished, status=200)
    out = _client().finish(session_id="s-1")
    assert out.status == "finished"
    assert responses.calls[0].request.method == "POST"


@responses.activate
def test_abort_posts_and_returns_session():
    aborted = {**_SESSION_JSON, "status": "aborted"}
    responses.add(responses.POST, f"{BASE}/upload_sessions/s-1/abort", json=aborted, status=200)
    out = _client().abort(session_id="s-1")
    assert out.status == "aborted"


@responses.activate
def test_abort_all_returns_status_ok():
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/abort_active_uploads",
        json={"status": "ok"},
        status=200,
    )
    out = _client().abort_all()
    assert isinstance(out, AbortActiveUploadsResult)
    assert out.status == "ok"
    assert responses.calls[0].request.method == "POST"
