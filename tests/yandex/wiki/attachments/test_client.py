import requests
import responses

from ycli.yandex.wiki.attachments.client import AttachmentsClient
from ycli.yandex.wiki.attachments.models import AttachmentList

BASE = "https://api.wiki.yandex.net/v1"


def _client():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return AttachmentsClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "f.pdf", "size": 1, "mime_type": "application/pdf"}]},
        status=200,
    )
    out = _client().list(page_id=42)
    assert isinstance(out, AttachmentList)
    assert [a.name for a in out.root] == ["f.pdf"]


@responses.activate
def test_list_attachments_for_page_id():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "f.pdf", "size": 1, "mime_type": "application/pdf"}]},
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
