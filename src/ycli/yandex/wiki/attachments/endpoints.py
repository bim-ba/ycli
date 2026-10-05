"""Wiki ``/pages/{id}/attachments``, declared once (sans-IO).

Examples:
    >>> download(7, 9).path
    'pages/7/attachments/9/download'
    >>> download_by_url("data/x/.files/d.png").params
    {'url': 'data/x/.files/d.png', 'download': 'true'}
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.attachments.models import (
    AttachedFile,
    Attachment,
    AttachmentCreate,
    AttachResponse,
)
from ycli.yandex.wiki.cursor import WIKI_CURSOR
from ycli.yandex.wiki.models import CursorPage


def list_(
    page_id: int, *, order_by: str | None, order_direction: str | None
) -> Paged[CursorPage[Attachment], Attachment]:
    path = f"pages/{segment(page_id)}/attachments"
    params = {"page_size": 100, "order_by": order_by, "order_direction": order_direction}
    return Paged(
        Endpoint(HTTPMethod.GET, path, CursorPage[Attachment], params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def get(page_id: int, file_id: int) -> Endpoint[AttachedFile]:
    """``GET /pages/{id}/attachments/{file_id}`` (undocumented): one attachment's metadata."""
    return Endpoint(
        HTTPMethod.GET, f"pages/{segment(page_id)}/attachments/{segment(file_id)}", AttachedFile
    )


def previews_download(page_id: int, file_id: int) -> Endpoint[bytes]:
    """``GET …/{file_id}/preview`` (undocumented): the preview image; base64 text if none."""
    path = f"pages/{segment(page_id)}/attachments/{segment(file_id)}/preview"
    return Endpoint(HTTPMethod.GET, path, bytes)


def download(page_id: int, file_id: int) -> Endpoint[bytes]:
    path = f"pages/{segment(page_id)}/attachments/{segment(file_id)}/download"
    return Endpoint(HTTPMethod.GET, path, bytes)


def download_by_url(url: str) -> Endpoint[bytes]:
    """``GET /pages/attachments/download_by_url`` — the API redirects to the file, followed."""
    params = {"url": url, "download": "true"}
    return Endpoint(HTTPMethod.GET, "pages/attachments/download_by_url", bytes, params=params)


def delete(page_id: int, file_id: int) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"pages/{segment(page_id)}/attachments/{segment(file_id)}")


def attach(page_id: int, body: AttachmentCreate) -> Endpoint[AttachResponse]:
    path = f"pages/{segment(page_id)}/attachments"
    return Endpoint(HTTPMethod.POST, path, AttachResponse, json=body)
