import json

import requests
import responses

from ycli.yandex.wiki.attachments.client import AttachmentsClient
from ycli.yandex.wiki.attachments.models import AttachedFileList, AttachmentList
from ycli.yandex.wiki.uploadsessions.client import UploadSessionsClient

BASE = "https://api.wiki.yandex.net/v1"


def _session():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


def _client():
    return AttachmentsClient(session=_session())


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "f.pdf", "size": "1.00", "mimetype": "application/pdf"}]},
        status=200,
    )
    out = _client().list(page_id=42)
    assert isinstance(out, AttachmentList)
    assert [a.name for a in out.root] == ["f.pdf"]


@responses.activate
def test_list_maps_string_size_and_mimetype():
    """Bug 5: real list payload carries ``size`` as a string and mime under ``mimetype``."""
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "shapecheck.txt", "size": "0.00", "mimetype": "text/plain"}]},
        status=200,
    )
    out = _client().list(page_id=42)
    assert out.root[0].size == "0.00"
    assert out.root[0].mimetype == "text/plain"


@responses.activate
def test_list_attachments_for_page_id():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "f.pdf", "size": "1.00", "mimetype": "application/pdf"}]},
        status=200,
    )
    out = _client().list(page_id=42)
    assert isinstance(out, AttachmentList)
    assert out.root[0].name == "f.pdf"
    assert responses.calls[0].request.params["page_size"] == "100"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_drains_next_cursor_across_pages():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "a.png"}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "b.png"}], "next_cursor": None},
        status=200,
    )
    out = _client().list(page_id=42)
    assert [a.name for a in out.root] == ["a.png", "b.png"]  # both pages drained
    assert len(responses.calls) == 2
    assert responses.calls[1].request.params["cursor"] == "c1"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_list_limit_truncates_without_second_fetch():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "a.png"}, {"name": "b.png"}], "next_cursor": "c1"},
        status=200,
    )
    out = _client().list(page_id=42, limit=1)
    assert [a.name for a in out.root] == ["a.png"]  # capped before draining c1
    assert len(responses.calls) == 1


@responses.activate
def test_download_returns_raw_bytes():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments/7/download",
        body=b"\x89PNG\r\n\x1a\n binary",
        status=200,
    )
    out = _client().download(page_id=42, file_id=7)
    assert out == b"\x89PNG\r\n\x1a\n binary"  # verbatim, no JSON parse
    assert responses.calls[0].request.url.endswith("/pages/42/attachments/7/download")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_download_by_url_returns_raw_bytes():
    responses.add(
        responses.GET,
        f"{BASE}/pages/attachments/download_by_url",
        body=b"%PDF-1.7 blob",
        status=200,
    )
    out = _client().download_by_url(url="data/x/.files/report.pdf")
    assert out == b"%PDF-1.7 blob"
    params = responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
    assert params["url"] == "data/x/.files/report.pdf"
    assert params["download"] == "true"


@responses.activate
def test_delete_sends_delete_and_returns_none():
    responses.add(
        responses.DELETE,
        f"{BASE}/pages/42/attachments/7",
        body="",
        status=204,
    )
    out = _client().delete(page_id=42, file_id=7)
    assert out is None  # 204 No Content — nothing to parse
    assert responses.calls[0].request.method == "DELETE"
    assert responses.calls[0].request.url.endswith("/pages/42/attachments/7")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_attach_posts_upload_sessions_body_and_flattens_results():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"id": 7, "name": "d.png", "mimetype": "image/png"}]},
        status=200,
    )
    out = _client().attach(page_id=42, session_ids=["s-1", "s-2"])
    assert isinstance(out, AttachedFileList)
    assert [f.id for f in out.root] == [7]
    assert out.root[0].mimetype == "image/png"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "upload_sessions": ["s-1", "s-2"]
    }


@responses.activate
def test_upload_runs_full_pipeline_in_order():
    session = _session()
    attachments = AttachmentsClient(session=session)
    sessions = UploadSessionsClient(session=session)

    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions",
        json={"session_id": "s-1", "status": "not_started"},
        status=200,
    )
    responses.add(
        responses.PUT,
        f"{BASE}/upload_sessions/s-1/upload_part",
        json={"session_id": "s-1", "status": "in_progress"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/s-1/finish",
        json={"session_id": "s-1", "status": "finished"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"id": 9, "name": "d.png"}]},
        status=200,
    )

    out = attachments.upload(sessions, 42, file_name="d.png", data=b"\x89PNGraw")
    assert isinstance(out, AttachedFileList)
    assert out.root[0].id == 9

    # the four pipeline calls fired in order: create → upload_part → finish → attach
    urls = [call.request.url for call in responses.calls]
    methods = [call.request.method for call in responses.calls]
    assert methods == ["POST", "PUT", "POST", "POST"]
    assert urls[0].endswith("/upload_sessions")  # ty: ignore[unresolved-attribute]
    assert "/upload_sessions/s-1/upload_part?part_number=1" in urls[1]  # ty: ignore[unsupported-operator]
    assert urls[2].endswith("/upload_sessions/s-1/finish")  # ty: ignore[unresolved-attribute]
    assert urls[3].endswith("/pages/42/attachments")  # ty: ignore[unresolved-attribute]

    # create body was sized to the payload; part carried the raw octet-stream bytes
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "file_name": "d.png",
        "file_size": 7,
    }
    assert responses.calls[1].request.body == b"\x89PNGraw"
    assert responses.calls[1].request.headers["Content-Type"] == "application/octet-stream"
    assert json.loads(responses.calls[3].request.body) == {  # ty: ignore[invalid-argument-type]
        "upload_sessions": ["s-1"]
    }
