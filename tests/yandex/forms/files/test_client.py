"""TDD for FilesClient — multipart upload, read-POST verify, binary download, DELETE body."""

import json

import requests
import responses

from ycli.yandex.forms.files.client import FilesClient
from ycli.yandex.forms.files.models import FileIn, FileList, FileOut
from ycli.yandex.models import Ack

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _client() -> FilesClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return FilesClient(session=session)


@responses.activate
def test_upload_sends_multipart_file_field():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/files",
        json={
            "name": "cv.pdf",
            "path": "a/b/cv.pdf",
            "size": 7,
            "url": "u",
            "check_status": "check",
        },
        status=201,
    )
    out = _client().upload(SID, filename="cv.pdf", data=b"%PDF123")
    assert isinstance(out, FileOut)
    assert out.path == "a/b/cv.pdf" and out.check_status == "check"
    request = responses.calls[0].request
    assert str(request.headers["Content-Type"]).startswith("multipart/form-data")
    body = request.body
    assert isinstance(body, bytes)
    assert b'name="file"' in body  # the multipart field is named "file"
    assert b'filename="cv.pdf"' in body  # the caller filename rides in the part
    assert b"%PDF123" in body  # the raw file bytes


@responses.activate
def test_verify_posts_file_list_and_returns_statuses():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/files/verify",
        json=[{"name": "cv.pdf", "path": "a/b/cv.pdf", "check_status": "ready"}],
        status=200,
    )
    out = _client().verify(SID, [FileIn(path="a/b/cv.pdf"), FileIn(url="https://x")])
    assert isinstance(out, FileList)
    assert out.root[0].check_status == "ready"
    assert json.loads(responses.calls[0].request.body) == [  # ty: ignore[invalid-argument-type]
        {"path": "a/b/cv.pdf"},
        {"url": "https://x"},
    ]  # only set fields are sent per item


@responses.activate
def test_download_returns_raw_bytes_with_query_params():
    responses.add(responses.GET, f"{BASE}/files", body=b"\x89PNGbytes", status=200)
    out = _client().download("a/b/cv.pdf", download=True, file_hash="h1")
    assert out == b"\x89PNGbytes"
    url = responses.calls[0].request.url
    assert url is not None
    assert "path=a%2Fb%2Fcv.pdf" in url
    assert "download=true" in url
    assert "hash=h1" in url  # file_hash maps to the ?hash= query key


@responses.activate
def test_download_omits_optional_query_when_unset():
    responses.add(responses.GET, f"{BASE}/files", body=b"data", status=200)
    _client().download("p")
    url = responses.calls[0].request.url
    assert url is not None
    assert "download=" not in url and "hash=" not in url  # unset options dropped


@responses.activate
def test_delete_sends_body_and_returns_ack():
    responses.add(responses.DELETE, f"{BASE}/files", json={}, status=200)
    out = _client().delete(path="a/b/cv.pdf", url="https://x")
    assert out == Ack(detail="deleted file path=a/b/cv.pdf url=https://x")
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "path": "a/b/cv.pdf",
        "url": "https://x",
    }
