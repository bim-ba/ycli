"""Forms file-storage operations, declared once (sans-IO).

Examples:
    >>> verify("686d", [{"path": "a/b.pdf"}]).effect
    <Effect.READ: 'read'>
"""

from __future__ import annotations

from http import HTTPMethod
from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Effect, Endpoint, segment
from ycli.yandex.forms.models import FileOut
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from ycli.yandex.forms.files.models import FileIn


def upload(survey_id: str, *, filename: str, data: bytes) -> Endpoint[FileOut]:
    path = f"surveys/{segment(survey_id)}/files"
    return Endpoint(HTTPMethod.POST, path, FileOut, files={"file": (filename, data)})


def verify(survey_id: str, body: ItemList[FileIn]) -> Endpoint[ItemList[FileOut]]:
    """``POST …/files/verify`` only reads the status of files already uploaded."""
    path = f"surveys/{segment(survey_id)}/files/verify"
    # violation(arch-3): POST verify only reads upload statuses
    return Endpoint(HTTPMethod.POST, path, ItemList[FileOut], json=body, effect=Effect.READ)


def download(path: str, *, download: bool | None, file_hash: str | None) -> Endpoint[bytes]:
    params = {"path": path, "download": download, "hash": file_hash}
    return Endpoint(HTTPMethod.GET, "files", bytes, params=params)


def delete(body: FileIn) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, "files", json=body)
