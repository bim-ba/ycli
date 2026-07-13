"""TDD for AttachmentsClient — responses stub + session DI (list JSON + binary downloads)."""

import requests
import responses

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.attachments.client import AttachmentsClient
from ycli.yandex.tracker.attachments.models import AttachmentList


def _client() -> AttachmentsClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return AttachmentsClient(session=session)


@responses.activate
def test_list_returns_attachments():
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/attachments",
        json=[{"id": "123", "name": "picture.jpg", "size": 19090, "mimetype": "image/jpg"}],
        status=200,
    )
    out = _client().list("JUNE-2")
    assert isinstance(out, AttachmentList)
    assert out.root[0].name == "picture.jpg"
    assert out.root[0].size == 19090


@responses.activate
def test_download_returns_raw_bytes():
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/attachments/4159/attachment.txt",
        body=b"\x89PNGbytes",
        status=200,
    )
    out = _client().download("JUNE-2", "4159", "attachment.txt")
    assert out == b"\x89PNGbytes"


@responses.activate
def test_download_thumbnail_returns_raw_bytes():
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/thumbnails/4159",
        body=b"\x89PNGthumb",
        status=200,
    )
    out = _client().download_thumbnail("JUNE-2", "4159")
    assert out == b"\x89PNGthumb"
