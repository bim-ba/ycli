"""Wiki ``/pages/{id}/attachments``, declared once (sans-IO).

Example:
    >>> download_attachment(7, 9).path
    'pages/7/attachments/9/download'
    >>> download_by_url("data/x/.files/d.png").params
    {'url': 'data/x/.files/d.png', 'download': 'true'}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.attachments.models import (
    AttachedFile,
    Attachment,
    AttachmentsResponse,
    AttachResponse,
)
from ycli.yandex.wiki.cursor import WIKI_CURSOR


def list_attachments(page_id: int) -> Paged[AttachmentsResponse, Attachment]:
    path = f"pages/{segment(page_id)}/attachments"
    return Paged(
        Endpoint("GET", path, AttachmentsResponse, params={"page_size": 100}),
        WIKI_CURSOR,
        lambda page: page.results,
    )


def get_attachment(page_id: int, file_id: int) -> Endpoint[AttachedFile]:
    """``GET /pages/{id}/attachments/{file_id}`` (undocumented): one attachment's metadata."""
    return Endpoint("GET", f"pages/{segment(page_id)}/attachments/{segment(file_id)}", AttachedFile)


def preview_attachment(page_id: int, file_id: int) -> Endpoint[bytes]:
    """``GET …/{file_id}/preview`` (undocumented): the preview image; base64 text if none."""
    path = f"pages/{segment(page_id)}/attachments/{segment(file_id)}/preview"
    return Endpoint("GET", path, bytes)


def download_attachment(page_id: int, file_id: int) -> Endpoint[bytes]:
    path = f"pages/{segment(page_id)}/attachments/{segment(file_id)}/download"
    return Endpoint("GET", path, bytes)


def download_by_url(url: str) -> Endpoint[bytes]:
    """``GET /pages/attachments/download_by_url`` — the API redirects to the file, followed."""
    params = {"url": url, "download": "true"}
    return Endpoint("GET", "pages/attachments/download_by_url", bytes, params=params)


def delete_attachment(page_id: int, file_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"pages/{segment(page_id)}/attachments/{segment(file_id)}")


def attach_files(page_id: int, body: dict[str, Any]) -> Endpoint[AttachResponse]:
    path = f"pages/{segment(page_id)}/attachments"
    return Endpoint("POST", path, AttachResponse, json=body)
